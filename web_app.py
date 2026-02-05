"""
API Web FastAPI para o Mamute
Interface web para navegadores
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import uuid
import os
import sys
from datetime import datetime

# Adicionar o diretório principal ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import IAPostgreSQL
from src.utils.logger import setup_logger
from src.utils.metrics import AdvancedMetricsManager
from src.utils.search import IntelligentSearchEngine, SearchType, SearchFilter, ContentType

# Modelos Pydantic para API
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    use_context: bool = True

class DocumentAdd(BaseModel):
    title: str
    content: str
    source: Optional[str] = None
    category: Optional[str] = None

class DatabaseQuery(BaseModel):
    query: str
    session_id: Optional[str] = None

class SessionStart(BaseModel):
    user_id: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    search_type: str = "hybrid"  # semantic, keyword, sql, hybrid
    content_type: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    min_similarity: float = 0.5
    max_results: int = 20

# Inicializar sistema
from contextlib import asynccontextmanager

logger = setup_logger("MamuteWeb", "INFO")
ia_system = None
metrics_manager = None
search_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global ia_system, metrics_manager, search_engine
    try:
        ia_system = IAPostgreSQL()
        ia_system.setup_database()
        metrics_manager = AdvancedMetricsManager(ia_system.db_manager, ia_system.config)
        search_engine = IntelligentSearchEngine(ia_system.db_manager, ia_system.embedding_manager, ia_system.config)
        logger.info("🐘 Mamute Web API iniciado com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao inicializar Mamute: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🐘 Mamute Web API finalizado")

# Inicializar FastAPI com lifespan
app = FastAPI(
    title="🐘 Mamute - IA PostgreSQL",
    description="Interface web para a IA Mamute especializada em PostgreSQL",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gerenciador de conexões WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.sessions: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "websocket": websocket,
                "created_at": datetime.now(),
                "message_count": 0
            }

    def disconnect(self, websocket: WebSocket, session_id: str):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if session_id in self.sessions:
            del self.sessions[session_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

# Rotas da API

@app.get("/", response_class=HTMLResponse)
async def home():
    """Dashboard principal do Mamute"""
    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <title>🐘 Mamute - IA PostgreSQL</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/static/mamute.css">
    </head>
    <body>
        <header class="header">
            <div class="header-content">
                <div class="logo">🐘 Mamute</div>
                <nav class="nav-menu">
                    <a href="/">Dashboard</a>
                    <a href="/chat">Chat</a>
                    <a href="/docs">API</a>
                </nav>
            </div>
        </header>

        <main class="main-container">
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">🎯</div>
                    <h1 class="card-title">Dashboard do Mamute</h1>
                </div>
                <p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">
                    Sua IA especialista em PostgreSQL e análise de dados
                </p>

                <!-- Status do Sistema -->
                <div class="grid grid-3" style="margin-bottom: 2rem;">
                    <div class="card">
                        <div class="card-header">
                            <div class="card-icon">🔗</div>
                            <div class="card-title">Sistema</div>
                        </div>
                        <div class="stats">
                            <div class="stat-item">
                                <span class="status online" id="systemStatus">Carregando...</span>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <div class="card-icon">🐘</div>
                            <div class="card-title">PostgreSQL</div>
                        </div>
                        <div class="stats">
                            <div class="stat-item">
                                <span class="status offline" id="dbStatus">Verificando...</span>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <div class="card-icon">📊</div>
                            <div class="card-title">Banco de Dados</div>
                        </div>
                        <div class="stats">
                            <div class="stat-item">
                                <span class="stat-label">Host:</span>
                                <span class="stat-value" id="dbHost" style="font-size: 1rem;">-</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Database:</span>
                                <span class="stat-value" id="dbName" style="font-size: 1rem;">-</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Ações Principais -->
                <div class="grid grid-2">
                    <div class="card">
                        <div class="card-header">
                            <div class="card-icon">💬</div>
                            <h3 class="card-title">Chat com Mamute</h3>
                        </div>
                        <p style="margin-bottom: 1.5rem;">Converse com a IA Mamute sobre seus dados PostgreSQL</p>
                        <a href="/chat" class="btn btn-primary">
                            <span class="btn-icon">🚀</span>
                            Iniciar Conversa
                        </a>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <div class="card-icon">📋</div>
                            <h3 class="card-title">Consulta SQL</h3>
                        </div>
                        <textarea 
                            id="sqlQuery" 
                            placeholder="SELECT * FROM sua_tabela LIMIT 10;" 
                            style="width: 100%; height: 80px; margin-bottom: 1rem; padding: 0.8rem; border: 2px solid #e9ecef; border-radius: 8px; font-family: monospace;">
                        </textarea>
                        <button onclick="DashboardUtils.executeQuery(document.getElementById('sqlQuery').value)" class="btn btn-secondary">
                            <span class="btn-icon">▶️</span>
                            Executar Consulta
                        </button>
                        <div id="queryResults" style="margin-top: 1rem;"></div>
                    </div>
                </div>

                <!-- Recursos Disponíveis -->
                <div class="card" style="margin-top: 2rem;">
                    <div class="card-header">
                        <div class="card-icon">🛠️</div>
                        <h3 class="card-title">Recursos do Mamute</h3>
                    </div>
                    <div class="grid grid-3">
                        <div style="text-align: center; padding: 1rem;">
                            <h4>🧠 Análise Inteligente</h4>
                            <p>Análise avançada de dados com insights automáticos</p>
                        </div>
                        <div style="text-align: center; padding: 1rem;">
                            <h4>🔍 Busca Semântica</h4>
                            <p>Busca inteligente em documentos usando embeddings</p>
                        </div>
                        <div style="text-align: center; padding: 1rem;">
                            <h4>📈 Relatórios</h4>
                            <p>Geração de relatórios e visualizações automatizadas</p>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <script src="/static/mamute.js"></script>
        <style>
            .results-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 1rem;
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .results-table th, .results-table td {
                padding: 0.8rem;
                text-align: left;
                border-bottom: 1px solid #e9ecef;
            }
            .results-table th {
                background: #667eea;
                color: white;
                font-weight: 600;
            }
            .results-table tr:hover {
                background: #f8f9fa;
            }
        </style>
    </body>
    </html>
    """

@app.get("/chat", response_class=HTMLResponse)
async def chat_page():
    """Interface de chat web aprimorada"""
    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <title>🐘 Chat com Mamute</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/static/mamute.css">
    </head>
    <body>
        <header class="header">
            <div class="header-content">
                <div class="logo">🐘 Chat com Mamute</div>
                <nav class="nav-menu">
                    <a href="/">Dashboard</a>
                    <a href="/chat">Chat</a>
                    <a href="/docs">API</a>
                </nav>
                <div class="status online" id="connectionStatus">Conectando...</div>
            </div>
        </header>

        <main class="main-container">
            <div class="card" style="padding: 0; height: 70vh;">
                <div class="chat-container">
                    <div class="chat-header">
                        <h2>🐘 Conversa com Mamute</h2>
                        <p>Sua IA especialista em PostgreSQL</p>
                    </div>
                    
                    <div class="chat-messages" id="chatMessages">
                        <!-- Mensagens aparecerão aqui -->
                    </div>
                    
                    <div class="chat-input">
                        <input 
                            type="text" 
                            id="messageInput" 
                            placeholder="Digite sua mensagem para Mamute..." 
                            disabled
                        >
                        <button id="sendButton" class="btn btn-primary" disabled>
                            Enviar
                        </button>
                    </div>
                </div>
            </div>

            <!-- Dicas de uso -->
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">💡</div>
                    <h3 class="card-title">Dicas para conversar com Mamute</h3>
                </div>
                <div class="grid grid-2">
                    <div>
                        <h4>🔍 Perguntas sobre dados:</h4>
                        <ul>
                            <li>"Quais tabelas estão disponíveis?"</li>
                            <li>"Analise os dados da tabela users"</li>
                            <li>"Mostre estatísticas da tabela vendas"</li>
                        </ul>
                    </div>
                    <div>
                        <h4>🛠️ Consultas SQL:</h4>
                        <ul>
                            <li>"Como otimizar esta consulta?"</li>
                            <li>"Crie uma consulta para relatório mensal"</li>
                            <li>"Explique este plano de execução"</li>
                        </ul>
                    </div>
                </div>
            </div>
        </main>

        <script src="/static/mamute.js"></script>
    </body>
    </html>
    """

@app.post("/session/start")
async def start_session(session_data: SessionStart):
    """Iniciar nova sessão"""
    if not ia_system:
        raise HTTPException(status_code=503, detail="Sistema não inicializado")
    
    try:
        session_id = ia_system.start_conversation(session_data.user_id)
        logger.info(f"Nova sessão web criada: {session_id}")
        
        return {
            "session_id": session_id,
            "message": "Sessão iniciada com sucesso",
            "mamute_name": ia_system.config.ai_name
        }
    except Exception as e:
        logger.error(f"Erro ao criar sessão: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(chat_data: ChatMessage):
    """Endpoint para conversar com Mamute (Modo Proativo)"""
    if not ia_system:
        raise HTTPException(status_code=503, detail="Sistema não inicializado")
    
    if not chat_data.session_id:
        # Criar sessão automaticamente se não fornecida
        session_id = ia_system.start_conversation()
    else:
        session_id = chat_data.session_id
    
    try:
        # Usar novo sistema de chat com personalidade e IA proativa
        if hasattr(ia_system, 'chat_personality') and ia_system.chat_personality:
            response = await ia_system.chat_personality.get_response(
                user_input=chat_data.message,
                context={
                    'session_id': session_id,
                    'use_context': chat_data.use_context,
                    'search_documents': True
                }
            )
            
            # Log detalhado para modo proativo
            proactive_info = ""
            if response.get('proactive_mode'):
                applied_improvements = response.get('applied_improvements', [])
                if applied_improvements:
                    proactive_info = f" | Melhorias: {len(applied_improvements)}"
                    logger.info(f"🚀 Modo Proativo - {len(applied_improvements)} melhorias aplicadas automaticamente!")
            
            logger.info(f"Chat Proativo - Sessão: {session_id}{proactive_info}")
            
            return {
                "response": response["response"],
                "session_id": session_id,
                "tokens_used": response.get("tokens_used", 0),
                "response_time": response.get("response_time", 0),
                "relevant_documents": response.get("relevant_documents", []),
                "mamute_name": ia_system.config.ai_name,
                "personality_mode": response.get("personality_mode", True),
                "proactive_mode": response.get("proactive_mode", False),
                "applied_improvements": response.get("applied_improvements", []),
                "suggested_improvements": response.get("suggested_improvements", []),
                "improvement_confidence": response.get("improvement_confidence", 0.0)
            }
        else:
            # Fallback para sistema original
            response = ia_system.chat_manager.send_message(
                message=chat_data.message, 
                session_id=session_id, 
                use_context=chat_data.use_context,
                search_documents=True
            )
            
            logger.info(f"Chat Fallback - Sessão: {session_id}, Tokens: {response.get('tokens_used', 0)}")
            
            return {
                "response": response["response"],
                "session_id": session_id,
                "tokens_used": response.get("tokens_used", 0),
                "response_time": response.get("response_time", 0),
                "relevant_documents": response.get("relevant_documents", []),
                "mamute_name": ia_system.config.ai_name
            }
        
    except Exception as e:
        logger.error(f"Erro no chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/proactive/toggle")
async def toggle_proactive_mode(enabled: Optional[bool] = None):
    """Ativar/Desativar modo proativo"""
    if not ia_system:
        raise HTTPException(status_code=503, detail="Sistema não inicializado")
    
    try:
        if hasattr(ia_system, 'chat_personality') and ia_system.chat_personality:
            current_mode = ia_system.chat_personality.toggle_proactive_mode(enabled)
            return {
                "proactive_mode": current_mode,
                "message": f"Modo proativo {'ativado' if current_mode else 'desativado'} com sucesso!",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=503, detail="Sistema de personalidade não disponível")
    except Exception as e:
        logger.error(f"Erro ao alterar modo proativo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/proactive/status")
async def get_proactive_status():
    """Obter status do modo proativo"""
    if not ia_system:
        raise HTTPException(status_code=503, detail="Sistema não inicializado")
    
    try:
        if hasattr(ia_system, 'chat_personality') and ia_system.chat_personality:
            return {
                "proactive_mode": getattr(ia_system.chat_personality, 'proactive_mode', False),
                "proactive_available": hasattr(ia_system.chat_personality, 'proactive_ai'),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "proactive_mode": False,
                "proactive_available": False,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Erro ao obter status proativo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents")
async def add_document(doc_data: DocumentAdd):
    """Adicionar documento ao sistema"""
    if not ia_system:
        raise HTTPException(status_code=503, detail="Sistema não inicializado")
    
    try:
        doc_id = ia_system.add_document(
            title=doc_data.title,
            content=doc_data.content,
            source=doc_data.source,
            category=doc_data.category
        )
        
        return {
            "document_id": doc_id,
            "message": "Documento adicionado com sucesso"
        }
        
    except Exception as e:
        logger.error(f"Erro ao adicionar documento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def execute_query(query_data: DatabaseQuery):
    """Executar consulta SQL (apenas SELECT)"""
    if not ia_system:
        raise HTTPException(status_code=503, detail="Sistema não inicializado")
    
    # Verificar se é uma query SELECT (segurança)
    if not query_data.query.strip().upper().startswith("SELECT"):
        raise HTTPException(
            status_code=400, 
            detail="Apenas consultas SELECT são permitidas"
        )
    
    try:
        results = ia_system.db_manager.execute_query(query_data.query)
        
        return {
            "results": results,
            "row_count": len(results) if results else 0,
            "query": query_data.query
        }
        
    except Exception as e:
        logger.error(f"Erro na consulta: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Verificar status do sistema"""
    if not ia_system:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": "Sistema não inicializado"}
        )
    
    try:
        # Testar conexão com banco
        db_connected = ia_system.db_manager.test_connection()
        
        return {
            "status": "healthy" if db_connected else "warning",
            "mamute_name": ia_system.config.ai_name,
            "database_connected": db_connected,
            "postgres_host": ia_system.config.postgres_host,
            "postgres_db": ia_system.config.postgres_db,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

@app.get("/metrics/advanced")
async def get_advanced_metrics():
    """Endpoint para métricas avançadas do dashboard"""
    if not metrics_manager:
        raise HTTPException(
            status_code=503, 
            detail="Sistema de métricas não inicializado"
        )
    
    try:
        metrics = metrics_manager.get_dashboard_metrics()
        return metrics
        
    except Exception as e:
        logger.error(f"Erro ao coletar métricas avançadas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/advanced", response_class=HTMLResponse)
async def advanced_dashboard():
    """Dashboard avançado com gráficos e métricas"""
    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <title>🐘 Mamute - Dashboard Avançado</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/static/mamute.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <header class="header">
            <div class="header-content">
                <div class="logo">🐘 Mamute Dashboard</div>
                <nav class="nav-menu">
                    <a href="/">Dashboard</a>
                    <a href="/dashboard/advanced">Avançado</a>
                    <a href="/chat">Chat</a>
                    <a href="/docs">API</a>
                </nav>
                <div class="dashboard-controls">
                    <label>
                        <input type="checkbox" id="autoRefresh" checked> Auto-refresh
                    </label>
                    <button id="refreshDashboard" class="btn btn-sm">🔄 Atualizar</button>
                </div>
            </div>
        </header>

        <main class="main-container advanced-dashboard">
            <!-- Alertas -->
            <div id="alertsContainer"></div>
            <div id="errorContainer"></div>

            <!-- Cards de Estatísticas Principais -->
            <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                <div class="stat-card">
                    <div class="stat-icon">💾</div>
                    <div class="stat-info">
                        <div class="stat-value" id="db-size">Carregando...</div>
                        <div class="stat-label">Tamanho do Banco</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📋</div>
                    <div class="stat-info">
                        <div class="stat-value" id="table-count">0</div>
                        <div class="stat-label">Tabelas</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">⚡</div>
                    <div class="stat-info">
                        <div class="stat-value" id="cache-hit-ratio">0%</div>
                        <div class="stat-label">Cache Hit Ratio</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🔗</div>
                    <div class="stat-info">
                        <div class="stat-value" id="active-connections">0</div>
                        <div class="stat-label">Conexões Ativas</div>
                    </div>
                </div>
            </div>

            <!-- Gráficos Principais -->
            <div class="charts-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 2rem; margin-bottom: 2rem;">
                
                <!-- Sistema de Saúde -->
                <div class="chart-card">
                    <div class="chart-header">
                        <h3>🏥 Saúde do Sistema</h3>
                        <small>Utilização de recursos</small>
                    </div>
                    <div class="chart-container">
                        <canvas id="systemHealthChart"></canvas>
                    </div>
                </div>

                <!-- Cache Hit Ratio -->
                <div class="chart-card">
                    <div class="chart-header">
                        <h3>💨 Cache Performance</h3>
                        <small>Taxa de acerto do cache</small>
                    </div>
                    <div class="chart-container">
                        <canvas id="cacheHitChart"></canvas>
                    </div>
                </div>

                <!-- Atividade do Banco -->
                <div class="chart-card">
                    <div class="chart-header">
                        <h3>📊 Atividade do Banco</h3>
                        <small>Últimas 24 horas</small>
                    </div>
                    <div class="chart-container">
                        <canvas id="dbActivityChart"></canvas>
                    </div>
                </div>

                <!-- Tipos de Conexões -->
                <div class="chart-card">
                    <div class="chart-header">
                        <h3>🔗 Conexões por Estado</h3>
                        <small>Distribuição atual</small>
                    </div>
                    <div class="chart-container">
                        <canvas id="connectionTypesChart"></canvas>
                    </div>
                </div>

            </div>

            <!-- Gráficos Secundários -->
            <div class="charts-secondary" style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem;">
                
                <!-- Performance Timeline -->
                <div class="chart-card">
                    <div class="chart-header">
                        <h3>⏱️ Performance ao Longo do Tempo</h3>
                        <small>Tempo de resposta e throughput</small>
                    </div>
                    <div class="chart-container">
                        <canvas id="performanceChart"></canvas>
                    </div>
                </div>

                <!-- Tamanhos das Tabelas -->
                <div class="chart-card">
                    <div class="chart-header">
                        <h3>📏 Maiores Tabelas</h3>
                        <small>Top 10 por tamanho</small>
                    </div>
                    <div class="chart-container">
                        <canvas id="tableSizesChart"></canvas>
                    </div>
                </div>

            </div>
        </main>

        <script src="/static/advanced-dashboard.js"></script>
        <style>
            .advanced-dashboard {
                padding: 2rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            
            .stat-card {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 12px;
                padding: 1.5rem;
                display: flex;
                align-items: center;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease;
            }
            
            .stat-card:hover {
                transform: translateY(-3px);
            }
            
            .stat-icon {
                font-size: 2.5rem;
                margin-right: 1rem;
            }
            
            .stat-value {
                font-size: 2rem;
                font-weight: bold;
                color: #667eea;
                line-height: 1;
            }
            
            .stat-label {
                color: #666;
                font-size: 0.9rem;
                margin-top: 0.2rem;
            }
            
            .chart-card {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 1.5rem;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            }
            
            .chart-header {
                margin-bottom: 1rem;
                padding-bottom: 0.5rem;
                border-bottom: 2px solid #f0f0f0;
            }
            
            .chart-header h3 {
                margin: 0;
                color: #333;
                font-size: 1.2rem;
            }
            
            .chart-header small {
                color: #666;
                font-size: 0.8rem;
            }
            
            .chart-container {
                height: 300px;
                position: relative;
            }
            
            .dashboard-controls {
                display: flex;
                align-items: center;
                gap: 1rem;
            }
            
            .dashboard-controls label {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: #333;
                font-size: 0.9rem;
            }
            
            .alert {
                padding: 1rem;
                border-radius: 8px;
                margin-bottom: 1rem;
                border-left: 4px solid;
            }
            
            .alert-warning {
                background: #fff3cd;
                border-color: #ffc107;
                color: #856404;
            }
            
            .alert-info {
                background: #d1ecf1;
                border-color: #17a2b8;
                color: #0c5460;
            }
            
            .alert-error {
                background: #f8d7da;
                border-color: #dc3545;
                color: #721c24;
            }
            
            .alert-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.5rem;
            }
            
            .alert-close {
                background: none;
                border: none;
                font-size: 1.2rem;
                cursor: pointer;
                color: inherit;
            }
        </style>
    </body>
    </html>
    """

@app.post("/search")
async def intelligent_search(search_request: SearchRequest):
    """Busca inteligente no sistema"""
    if not search_engine:
        raise HTTPException(
            status_code=503, 
            detail="Sistema de busca não inicializado"
        )
    
    try:
        # Converter string para enum
        search_type = SearchType(search_request.search_type)
        
        # Criar filtros
        filters = SearchFilter(
            content_type=ContentType(search_request.content_type) if search_request.content_type else None,
            category=search_request.category,
            source=search_request.source,
            min_similarity=search_request.min_similarity,
            max_results=search_request.max_results
        )
        
        # Executar busca
        results = search_engine.search(search_request.query, search_type, filters)
        
        # Converter resultados para dicionários
        results_dict = [result.to_dict() for result in results]
        
        return {
            "query": search_request.query,
            "search_type": search_request.search_type,
            "total_results": len(results_dict),
            "results": results_dict
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Parâmetro inválido: {e}")
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/suggestions")
async def search_suggestions(q: str, limit: int = 10):
    """Sugestões de busca"""
    if not search_engine:
        raise HTTPException(
            status_code=503, 
            detail="Sistema de busca não inicializado"
        )
    
    try:
        suggestions = search_engine.get_search_suggestions(q, limit)
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"Erro ao gerar sugestões: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/stats")
async def search_stats():
    """Estatísticas do sistema de busca"""
    if not search_engine:
        raise HTTPException(
            status_code=503, 
            detail="Sistema de busca não inicializado"
        )
    
    try:
        stats = search_engine.get_search_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de busca: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search", response_class=HTMLResponse)
async def search_page():
    """Página de busca avançada"""
    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <title>🔍 Busca Inteligente - Mamute</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/static/mamute.css">
    </head>
    <body>
        <header class="header">
            <div class="header-content">
                <div class="logo">🔍 Busca Inteligente</div>
                <nav class="nav-menu">
                    <a href="/">Dashboard</a>
                    <a href="/dashboard/advanced">Avançado</a>
                    <a href="/chat">Chat</a>
                    <a href="/search">Busca</a>
                    <a href="/docs">API</a>
                </nav>
            </div>
        </header>

        <main class="main-container">
            <!-- Busca Principal -->
            <div class="search-container">
                <div class="search-header">
                    <h1>🧠 Busca Inteligente do Mamute</h1>
                    <p>Busque em documentos, conversas, consultas SQL e muito mais!</p>
                </div>

                <div class="search-box">
                    <div class="search-input-group">
                        <input type="text" id="searchQuery" placeholder="Digite sua busca aqui..." autocomplete="off">
                        <button id="searchButton" class="btn btn-primary">🔍 Buscar</button>
                    </div>
                    
                    <div class="search-suggestions" id="searchSuggestions" style="display: none;"></div>
                </div>

                <!-- Filtros -->
                <div class="search-filters">
                    <div class="filter-group">
                        <label>Tipo de Busca:</label>
                        <select id="searchType">
                            <option value="hybrid">🔄 Híbrida (Recomendada)</option>
                            <option value="semantic">🧠 Semântica</option>
                            <option value="keyword">🔤 Palavras-chave</option>
                            <option value="sql">💾 Resultados SQL</option>
                        </select>
                    </div>

                    <div class="filter-group">
                        <label>Tipo de Conteúdo:</label>
                        <select id="contentType">
                            <option value="">Todos</option>
                            <option value="document">📄 Documentos</option>
                            <option value="conversation">💬 Conversas</option>
                            <option value="query_result">📊 Resultados SQL</option>
                            <option value="log_entry">📝 Logs</option>
                        </select>
                    </div>

                    <div class="filter-group">
                        <label>Similaridade Mínima:</label>
                        <input type="range" id="minSimilarity" min="0" max="1" step="0.1" value="0.5">
                        <span id="similarityValue">0.5</span>
                    </div>

                    <div class="filter-group">
                        <label>Max Resultados:</label>
                        <input type="number" id="maxResults" value="20" min="1" max="100">
                    </div>
                </div>
            </div>

            <!-- Resultados -->
            <div class="search-results" id="searchResults"></div>

            <!-- Estatísticas -->
            <div class="search-stats" id="searchStats"></div>
        </main>

        <script src="/static/search.js"></script>
        <style>
            .search-container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 2rem;
                margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            }

            .search-header {
                text-align: center;
                margin-bottom: 2rem;
            }

            .search-header h1 {
                color: #667eea;
                margin-bottom: 0.5rem;
            }

            .search-input-group {
                display: flex;
                gap: 1rem;
                margin-bottom: 1rem;
            }

            .search-input-group input {
                flex: 1;
                padding: 1rem;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                font-size: 1.1rem;
            }

            .search-input-group input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }

            .search-suggestions {
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                max-height: 200px;
                overflow-y: auto;
                position: relative;
                z-index: 100;
            }

            .suggestion-item {
                padding: 0.8rem;
                cursor: pointer;
                border-bottom: 1px solid #f8f9fa;
            }

            .suggestion-item:hover {
                background: #f8f9fa;
            }

            .search-filters {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                padding: 1rem;
                background: #f8f9fa;
                border-radius: 10px;
                margin-top: 1rem;
            }

            .filter-group {
                display: flex;
                flex-direction: column;
            }

            .filter-group label {
                font-weight: 600;
                margin-bottom: 0.5rem;
                color: #333;
            }

            .filter-group input, .filter-group select {
                padding: 0.5rem;
                border: 1px solid #ddd;
                border-radius: 5px;
            }

            .search-results {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 2rem;
                margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            }

            .result-item {
                padding: 1.5rem;
                border-bottom: 1px solid #e9ecef;
                transition: background 0.3s ease;
            }

            .result-item:hover {
                background: #f8f9fa;
            }

            .result-title {
                font-size: 1.2rem;
                font-weight: 600;
                color: #667eea;
                margin-bottom: 0.5rem;
            }

            .result-content {
                color: #333;
                line-height: 1.6;
                margin-bottom: 1rem;
            }

            .result-meta {
                display: flex;
                gap: 1rem;
                font-size: 0.9rem;
                color: #666;
            }

            .result-similarity {
                background: #28a745;
                color: white;
                padding: 0.2rem 0.5rem;
                border-radius: 15px;
                font-weight: 600;
            }

            .search-stats {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 1.5rem;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            }
        </style>
    </body>
    </html>
    """

@app.post("/upload/document")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form(None),
    source: str = Form(None)
):
    """Upload de documento para o sistema"""
    if not ia_system:
        raise HTTPException(
            status_code=503, 
            detail="Sistema não inicializado"
        )
    
    try:
        # Verificar tipo de arquivo
        allowed_types = ['text/plain', 'text/markdown', 'text/csv', 'application/json', 'application/pdf']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de arquivo não suportado: {file.content_type}"
            )
        
        # Ler conteúdo do arquivo
        content = await file.read()
        
        # Decodificar conteúdo baseado no tipo
        if file.content_type == 'application/pdf':
            # Para PDF seria necessário uma biblioteca específica
            text_content = "Conteúdo PDF (processamento não implementado)"
        else:
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text_content = content.decode('latin-1')
                except UnicodeDecodeError:
                    text_content = content.decode('utf-8', errors='ignore')
        
        # Validar tamanho do conteúdo
        if len(text_content) > 1000000:  # 1MB de texto
            raise HTTPException(
                status_code=400,
                detail="Arquivo muito grande (máximo 1MB de texto)"
            )
        
        # Adicionar documento ao sistema
        document_id = ia_system.embedding_manager.add_document(
            title=title,
            content=text_content,
            source=source or file.filename,
            category=category,
            metadata={
                'filename': file.filename,
                'content_type': file.content_type,
                'size': len(content),
                'uploaded_at': datetime.now().isoformat()
            }
        )
        
        # Adicionar ao índice de busca
        if search_engine:
            search_engine.add_to_search_index(
                content_type=ContentType.DOCUMENT,
                title=title,
                content=text_content,
                source=source or file.filename,
                category=category,
                metadata={
                    'document_id': document_id,
                    'filename': file.filename,
                    'content_type': file.content_type
                }
            )
        
        return {
            "success": True,
            "document_id": document_id,
            "title": title,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content),
            "content_length": len(text_content),
            "message": "Documento enviado e indexado com sucesso!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload/bulk")
async def upload_bulk_documents(files: List[UploadFile] = File(...)):
    """Upload múltiplo de documentos"""
    if not ia_system:
        raise HTTPException(
            status_code=503, 
            detail="Sistema não inicializado"
        )
    
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Máximo 10 arquivos por vez"
        )
    
    results = []
    errors = []
    
    for file in files:
        try:
            # Usar o filename como título
            title = file.filename.rsplit('.', 1)[0]  # Remove extensão
            
            # Upload individual
            content = await file.read()
            
            # Verificar tipo
            if file.content_type not in ['text/plain', 'text/markdown', 'text/csv', 'application/json']:
                errors.append({
                    'filename': file.filename,
                    'error': f'Tipo não suportado: {file.content_type}'
                })
                continue
            
            # Decodificar
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                text_content = content.decode('utf-8', errors='ignore')
            
            # Adicionar documento
            document_id = ia_system.embedding_manager.add_document(
                title=title,
                content=text_content,
                source=file.filename,
                metadata={
                    'filename': file.filename,
                    'content_type': file.content_type,
                    'size': len(content),
                    'uploaded_at': datetime.now().isoformat(),
                    'bulk_upload': True
                }
            )
            
            results.append({
                'filename': file.filename,
                'document_id': document_id,
                'title': title,
                'success': True
            })
            
        except Exception as e:
            errors.append({
                'filename': file.filename,
                'error': str(e)
            })
    
    return {
        'total_files': len(files),
        'successful_uploads': len(results),
        'failed_uploads': len(errors),
        'results': results,
        'errors': errors
    }

@app.get("/documents")
async def list_documents(
    page: int = 1,
    limit: int = 20,
    category: str = None,
    source: str = None
):
    """Lista documentos cadastrados"""
    if not ia_system:
        raise HTTPException(
            status_code=503, 
            detail="Sistema não inicializado"
        )
    
    try:
        # Construir query com filtros
        conditions = []
        params = []
        
        if category:
            conditions.append("category = %s")
            params.append(category)
        
        if source:
            conditions.append("source ILIKE %s")
            params.append(f"%{source}%")
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        # Query para total de documentos
        count_query = f"SELECT COUNT(*) as total FROM documents {where_clause}"
        count_result = ia_system.db_manager.execute_query(count_query, params)
        total_documents = count_result[0]['total'] if count_result else 0
        
        # Query para documentos da página
        offset = (page - 1) * limit
        params.extend([limit, offset])
        
        documents_query = f"""
            SELECT id, title, source, category, 
                   LENGTH(content) as content_length,
                   created_at, metadata
            FROM documents {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        
        documents = ia_system.db_manager.execute_query(documents_query, params)
        
        # Calcular informações de paginação
        total_pages = (total_documents + limit - 1) // limit
        
        return {
            'documents': documents,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_documents': total_documents,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar documentos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Deleta um documento"""
    if not ia_system:
        raise HTTPException(
            status_code=503, 
            detail="Sistema não inicializado"
        )
    
    try:
        # Verificar se documento existe
        check_query = "SELECT id, title FROM documents WHERE id = %s"
        document = ia_system.db_manager.execute_query(check_query, (document_id,))
        
        if not document:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        
        # Deletar documento
        delete_query = "DELETE FROM documents WHERE id = %s"
        ia_system.db_manager.execute_query(delete_query, (document_id,))
        
        return {
            'success': True,
            'message': f'Documento "{document[0]["title"]}" deletado com sucesso'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar documento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/upload", response_class=HTMLResponse)
async def upload_page():
    """Página de upload de documentos"""
    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <title>📤 Upload de Documentos - Mamute</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/static/mamute.css">
    </head>
    <body>
        <header class="header">
            <div class="header-content">
                <div class="logo">📤 Upload de Documentos</div>
                <nav class="nav-menu">
                    <a href="/">Dashboard</a>
                    <a href="/dashboard/advanced">Avançado</a>
                    <a href="/chat">Chat</a>
                    <a href="/search">Busca</a>
                    <a href="/upload">Upload</a>
                    <a href="/docs">API</a>
                </nav>
            </div>
        </header>

        <main class="main-container">
            <!-- Upload Individual -->
            <div class="upload-section">
                <div class="upload-header">
                    <h1>📤 Enviar Documentos para o Mamute</h1>
                    <p>Adicione documentos ao banco de conhecimento para busca e análise</p>
                </div>

                <div class="upload-form-container">
                    <form id="uploadForm" class="upload-form">
                        <div class="form-group">
                            <label for="documentFile">📁 Arquivo:</label>
                            <input type="file" id="documentFile" name="file" 
                                   accept=".txt,.md,.csv,.json,.pdf" required>
                            <small>Formatos suportados: TXT, MD, CSV, JSON, PDF</small>
                        </div>

                        <div class="form-group">
                            <label for="documentTitle">🏷️ Título:</label>
                            <input type="text" id="documentTitle" name="title" 
                                   placeholder="Digite o título do documento" required>
                        </div>

                        <div class="form-group">
                            <label for="documentCategory">📂 Categoria:</label>
                            <select id="documentCategory" name="category">
                                <option value="">Selecionar categoria (opcional)</option>
                                <option value="manual">Manual/Documentação</option>
                                <option value="tutorial">Tutorial</option>
                                <option value="reference">Referência</option>
                                <option value="data">Dados</option>
                                <option value="report">Relatório</option>
                                <option value="other">Outro</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="documentSource">🔗 Fonte:</label>
                            <input type="text" id="documentSource" name="source" 
                                   placeholder="URL ou fonte do documento (opcional)">
                        </div>

                        <button type="submit" class="btn btn-primary">
                            📤 Enviar Documento
                        </button>
                    </form>
                </div>
            </div>

            <!-- Upload Múltiplo -->
            <div class="bulk-upload-section">
                <div class="section-header">
                    <h2>📁 Upload Múltiplo</h2>
                    <p>Envie vários arquivos de uma só vez (máximo 10)</p>
                </div>

                <div class="bulk-upload-area" id="bulkUploadArea">
                    <div class="upload-drop-zone" id="dropZone">
                        <div class="drop-zone-content">
                            <div class="drop-icon">📁</div>
                            <h3>Arraste arquivos aqui</h3>
                            <p>ou clique para selecionar</p>
                            <input type="file" id="bulkFiles" multiple 
                                   accept=".txt,.md,.csv,.json" style="display: none;">
                        </div>
                    </div>

                    <div class="selected-files" id="selectedFiles"></div>
                    
                    <button id="bulkUploadBtn" class="btn btn-secondary" style="display: none;">
                        🚀 Enviar Todos os Arquivos
                    </button>
                </div>
            </div>

            <!-- Lista de Documentos -->
            <div class="documents-section">
                <div class="section-header">
                    <h2>📚 Documentos Cadastrados</h2>
                    <div class="documents-controls">
                        <input type="text" id="searchDocuments" placeholder="Filtrar documentos...">
                        <button id="refreshDocuments" class="btn btn-sm">🔄 Atualizar</button>
                    </div>
                </div>

                <div class="documents-list" id="documentsList">
                    <!-- Lista será carregada dinamicamente -->
                </div>

                <div class="pagination-container" id="paginationContainer">
                    <!-- Paginação será carregada dinamicamente -->
                </div>
            </div>

            <!-- Progress Modal -->
            <div class="modal" id="uploadModal" style="display: none;">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>📤 Enviando Documentos</h3>
                    </div>
                    <div class="modal-body">
                        <div class="progress-bar" id="uploadProgress">
                            <div class="progress-fill"></div>
                        </div>
                        <div class="progress-text" id="progressText">Preparando upload...</div>
                    </div>
                </div>
            </div>
        </main>

        <script src="/static/upload.js"></script>
        <style>
            .upload-section, .bulk-upload-section, .documents-section {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 2rem;
                margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            }

            .upload-header, .section-header {
                text-align: center;
                margin-bottom: 2rem;
            }

            .upload-header h1, .section-header h2 {
                color: #667eea;
                margin-bottom: 0.5rem;
            }

            .upload-form {
                max-width: 600px;
                margin: 0 auto;
            }

            .form-group {
                margin-bottom: 1.5rem;
            }

            .form-group label {
                display: block;
                font-weight: 600;
                margin-bottom: 0.5rem;
                color: #333;
            }

            .form-group input, .form-group select {
                width: 100%;
                padding: 0.8rem;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                font-size: 1rem;
            }

            .form-group input:focus, .form-group select:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }

            .form-group small {
                color: #666;
                font-size: 0.8rem;
            }

            .upload-drop-zone {
                border: 3px dashed #667eea;
                border-radius: 15px;
                padding: 3rem;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-bottom: 1rem;
            }

            .upload-drop-zone:hover, .upload-drop-zone.drag-over {
                border-color: #4facfe;
                background: rgba(102, 126, 234, 0.05);
            }

            .drop-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }

            .drop-zone-content h3 {
                color: #667eea;
                margin-bottom: 0.5rem;
            }

            .selected-files {
                margin: 1rem 0;
            }

            .file-item {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0.8rem;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                margin-bottom: 0.5rem;
            }

            .file-info {
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            .file-remove {
                background: #dc3545;
                color: white;
                border: none;
                border-radius: 50%;
                width: 25px;
                height: 25px;
                cursor: pointer;
            }

            .documents-controls {
                display: flex;
                gap: 1rem;
                align-items: center;
                margin-bottom: 1rem;
            }

            .documents-controls input {
                flex: 1;
                padding: 0.5rem;
                border: 1px solid #ddd;
                border-radius: 5px;
            }

            .document-item {
                padding: 1rem;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                margin-bottom: 0.5rem;
                transition: background 0.3s ease;
            }

            .document-item:hover {
                background: #f8f9fa;
            }

            .document-header {
                display: flex;
                justify-content: between;
                align-items: center;
                margin-bottom: 0.5rem;
            }

            .document-title {
                font-weight: 600;
                color: #667eea;
            }

            .document-meta {
                display: flex;
                gap: 1rem;
                font-size: 0.8rem;
                color: #666;
            }

            .document-actions {
                display: flex;
                gap: 0.5rem;
            }

            .modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 1000;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .modal-content {
                background: white;
                border-radius: 15px;
                padding: 2rem;
                max-width: 500px;
                width: 90%;
            }

            .progress-bar {
                width: 100%;
                height: 20px;
                background: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
                margin: 1rem 0;
            }

            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                width: 0%;
                transition: width 0.3s ease;
            }

            .progress-text {
                text-align: center;
                color: #666;
            }
        </style>
    </body>
    </html>
    """

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket para chat em tempo real"""
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Processar mensagem com Mamute
            if ia_system:
                response = ia_system.chat_manager.send_message(
                    message=message_data["message"], 
                    session_id=session_id,
                    use_context=True,
                    search_documents=True
                )
                
                # Enviar resposta
                await manager.send_personal_message(
                    json.dumps({
                        "type": "response",
                        "response": response["response"],
                        "tokens_used": response.get("tokens_used", 0),
                        "response_time": response.get("response_time", 0),
                        "mamute_name": ia_system.config.ai_name
                    }),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
        logger.info(f"WebSocket desconectado: {session_id}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "web_app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )