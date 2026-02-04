"""
API Web FastAPI para o Mamute
Interface web para navegadores
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
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

# Inicializar sistema
from contextlib import asynccontextmanager

logger = setup_logger("MamuteWeb", "INFO")
ia_system = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global ia_system
    try:
        ia_system = IAPostgreSQL()
        ia_system.setup_database()
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
    """Endpoint para conversar com Mamute"""
    if not ia_system:
        raise HTTPException(status_code=503, detail="Sistema não inicializado")
    
    if not chat_data.session_id:
        # Criar sessão automaticamente se não fornecida
        session_id = ia_system.start_conversation()
    else:
        session_id = chat_data.session_id
    
    try:
        response = ia_system.chat_manager.send_message(
            message=chat_data.message, 
            session_id=session_id, 
            use_context=chat_data.use_context,
            search_documents=True
        )
        
        logger.info(f"Chat web - Sessão: {session_id}, Tokens: {response.get('tokens_used', 0)}")
        
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