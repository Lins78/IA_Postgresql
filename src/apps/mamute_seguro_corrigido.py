"""
IA Mamute - Versão Ultra-Segura CORRIGIDA (Sem loops de redirecionamento)
"""
from fastapi import FastAPI, HTTPException, Request, Depends, Cookie, status, File, UploadFile, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
import time
import json
import uvicorn
import base64
import mimetypes
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# Adicionar o diretório principal ao path
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
APPS_DIR = SRC_DIR / "apps"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

# Importar IA COMPLETA
try:
    from main import IAPostgreSQL
    from src.ai.chat import MamuteChat
    from src.ai.agent import IAAgent
    from src.utils.logger import setup_logger
    ia_system = IAPostgreSQL()
    ia_disponivel = True
    print("✅ IA COMPLETA carregada com sucesso!")
except Exception as e:
    print(f"⚠️ IA simplificada - Erro ao carregar sistema completo: {e}")
    ia_system = None
    ia_disponivel = False
security = HTTPBasic()

# Importar IA principal se disponível
try:
    from main import IAPostgreSQL
    from src.ai.agent import AIAgent
    from src.ai.chat import IntelligentChat
    from src.ai.fallback_chat import FallbackChat
    from src.utils.logger import setup_logger
    ia_principal_disponivel = True
    print("✅ IA Principal importada com sucesso!")
except Exception as e:
    ia_principal_disponivel = False
    print(f"⚠️ IA Principal não disponível: {e}")

# Inicializar IA principal se disponível
ia_instance = None
if ia_principal_disponivel:
    try:
        ia_instance = IAPostgreSQL()
        print("✅ IA PostgreSQL inicializada!")
    except:
        print("⚠️ Erro ao inicializar IA PostgreSQL")

class SimpleSecurityManager:
    def __init__(self):
        self.pending_requests = {}
        self.approved_sessions = {}
        self.blocked_ips = set()
        self.access_logs = []
        
    def create_access_request(self, client_ip: str, user_agent: str, path: str) -> str:
        request_id = str(uuid.uuid4())
        self.pending_requests[request_id] = {
            'id': request_id,
            'ip': client_ip,
            'user_agent': user_agent,
            'path': path,
            'timestamp': datetime.now(),
            'status': 'pending',
        }
        
        print(f"""
🚨 NOVA SOLICITAÇÃO DE ACESSO!
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 IP: {client_ip}
🖥️ Dispositivo: {user_agent[:50]}...
📄 Página: {path}
🆔 ID: {request_id}
⏰ {datetime.now().strftime('%H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """)
        
        return request_id
        
    def approve_request(self, request_id: str) -> Optional[str]:
        if request_id not in self.pending_requests:
            return None
            
        req = self.pending_requests[request_id]
        session_id = str(uuid.uuid4())
        
        self.approved_sessions[session_id] = {
            'ip': req['ip'],
            'approved_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=1),
            'request_id': request_id
        }
        
        req['status'] = 'approved'
        req['session_id'] = session_id
        
        print(f"✅ ACESSO APROVADO: {req['ip']} - Sessão: {session_id}")
        return session_id
        
    def deny_request(self, request_id: str) -> bool:
        if request_id not in self.pending_requests:
            return False
            
        req = self.pending_requests[request_id]
        req['status'] = 'denied'
        self.blocked_ips.add(req['ip'])
        
        print(f"❌ ACESSO NEGADO: {req['ip']} - IP BLOQUEADO")
        return True
        
    def is_session_valid(self, session_id: str, client_ip: str) -> bool:
        if not session_id or session_id not in self.approved_sessions:
            return False
            
        session = self.approved_sessions[session_id]
        
        if session['ip'] != client_ip:
            return False
            
        if datetime.now() > session['expires_at']:
            del self.approved_sessions[session_id]
            return False
            
        return True
        
    def authenticate_admin(self, credentials: HTTPBasicCredentials) -> bool:
        return credentials.username == "admin" and credentials.password == "mamute2026"

security_manager = SimpleSecurityManager()

app = FastAPI(title="🔒 IA Mamute Ultra-Segura", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos
if os.path.exists("web/static"):
    app.mount("/static", StaticFiles(directory="web/static"), name="static")

class AdminAction(BaseModel):
    action: str
    request_id: str

class ChatMessage(BaseModel):
    message: str
    image_data: Optional[str] = None  # Base64 encoded image
    image_filename: Optional[str] = None

class ImageUpload(BaseModel):
    filename: str
    data: str  # Base64 encoded
    content_type: str

# Criar diretório para uploads se não existir
UPLOADS_DIR = "uploads/images"
os.makedirs(UPLOADS_DIR, exist_ok=True)

# ============================================================================
# ENDPOINTS PRINCIPAIS
# ============================================================================

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...), mamute_session: str = Cookie(None)):
    if not mamute_session:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    
    # Verificar tipo de arquivo
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado. Use JPG, PNG, GIF ou WebP.")
    
    # Verificar tamanho (max 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo 10MB.")
    
    # Gerar nome único
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # Salvar arquivo
    file_path = os.path.join(UPLOADS_DIR, unique_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Converter para base64 para envio
    base64_data = base64.b64encode(content).decode('utf-8')
    
    return {
        "filename": unique_filename,
        "original_name": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "base64_data": base64_data,
        "url": f"/images/{unique_filename}"
    }

@app.get("/images/{filename}")
async def get_image(filename: str):
    file_path = os.path.join(UPLOADS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    # Detectar tipo de conteúdo
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "application/octet-stream"
    
    with open(file_path, "rb") as f:
        return Response(content=f.read(), media_type=content_type)

# ============================================================================
# ENDPOINTS PARA UPLOAD DE IMAGENS
# ============================================================================

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...), mamute_session: str = Cookie(None)):
    if not mamute_session:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    
    # Verificar tipo de arquivo
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado. Use JPG, PNG, GIF ou WebP.")
    
    # Verificar tamanho (max 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo 10MB.")
    
    # Gerar nome único
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # Salvar arquivo
    file_path = os.path.join(UPLOADS_DIR, unique_filename)
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Converter para base64 para envio
    base64_data = base64.b64encode(content).decode('utf-8')
    
    return {
        "filename": unique_filename,
        "original_name": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "base64_data": base64_data,
        "url": f"/images/{unique_filename}"
    }

@app.get("/images/{filename}")
async def get_image(filename: str):
    file_path = os.path.join(UPLOADS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    # Detectar tipo de conteúdo
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "application/octet-stream"
    
    with open(file_path, "rb") as f:
        return Response(content=f.read(), media_type=content_type)

@app.get("/")
async def home(request: Request, mamute_session: str = Cookie(None)):
    client_ip = request.client.host
    
    # Verificar se tem sessão válida
    if mamute_session and security_manager.is_session_valid(mamute_session, client_ip):
        return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>🤖 IA Mamute - Acesso Autorizado</title>
    <meta charset="utf-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            text-align: center; 
            padding: 50px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container { 
            background: rgba(255,255,255,0.1); 
            padding: 40px; 
            border-radius: 20px; 
            backdrop-filter: blur(10px);
        }
        .btn {
            background: white;
            color: #667eea;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1.1em;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 IA Mamute Ultra-Segura</h1>
        <p>✅ Acesso autorizado pelo administrador</p>
        <p>Bem-vindo à IA mais segura do mundo!</p>
        
        <div>
            <a href="/chat" class="btn">💬 Chat com IA</a>
            <a href="/admin" class="btn">🔒 Painel Admin</a>
        </div>
        
        <br><br>
        <small>Sua sessão expira em 1 hora por segurança</small>
    </div>
</body>
</html>
        """)
    else:
        # Redirecionar para solicitar acesso
        return RedirectResponse(url="/request-access")

@app.get("/request-access")
async def request_access(request: Request):
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    
    request_id = security_manager.create_access_request(client_ip, user_agent, "/")
    
    return HTMLResponse(f"""
<!DOCTYPE html>
<html>
<head>
    <title>🔒 Solicitar Acesso - IA Mamute</title>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 500px;
        }}
        .btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1.1em;
            margin: 10px;
            text-decoration: none;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div style="font-size: 4em;">🔒</div>
        <h1>Solicitar Acesso</h1>
        <p>Para acessar a IA Mamute, você precisa de autorização.</p>
        
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <strong>📍 Seu IP:</strong> {client_ip}<br>
            <strong>🆔 ID da Solicitação:</strong> {request_id}<br>
            <strong>⏰ Hora:</strong> {datetime.now().strftime('%H:%M:%S')}
        </div>
        
        <a href="/wait-approval?request_id={request_id}" class="btn">
            ⏳ Aguardar Aprovação
        </a>
        
        <p style="color: #666; margin-top: 20px;">
            O administrador foi notificado sobre sua solicitação.
        </p>
    </div>
</body>
</html>
    """)

@app.get("/wait-approval")
async def wait_approval(request_id: str):
    if request_id not in security_manager.pending_requests:
        return RedirectResponse(url="/request-access")
    
    req = security_manager.pending_requests[request_id]
    
    if req['status'] == 'approved':
        session_id = req.get('session_id')
        response = RedirectResponse(url="/")
        response.set_cookie("mamute_session", session_id, max_age=3600)
        return response
    elif req['status'] == 'denied':
        return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>❌ Acesso Negado</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #ff6b6b; color: white; }
    </style>
</head>
<body>
    <h1>❌ Acesso Negado</h1>
    <p>Sua solicitação foi negada pelo administrador.</p>
</body>
</html>
        """)
    
    return HTMLResponse(f"""
<!DOCTYPE html>
<html>
<head>
    <title>⏳ Aguardando Aprovação</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body {{
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }}
    </style>
</head>
<body>
    <div style="font-size: 4em;">⏳</div>
    <h1>Aguardando Aprovação</h1>
    <p>Status: {req['status'].title()}</p>
    <p>Solicitado em: {req['timestamp'].strftime('%H:%M:%S')}</p>
    <p>A página será atualizada automaticamente.</p>
</body>
</html>
    """)

@app.get("/chat")
async def chat_interface(mamute_session: str = Cookie(None)):
    if not mamute_session:
        return RedirectResponse(url="/request-access")
        
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>💬 Chat IA Mamute</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: rgba(255,255,255,0.1);
            color: white;
            padding: 15px 20px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .security-badge {
            background: #28a745;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            margin-bottom: 10px;
            display: inline-block;
        }
        
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 1000px;
            margin: 20px auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            max-height: 500px;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 18px;
            max-width: 80%;
            word-wrap: break-word;
        }
        
        .user-message {
            background: #667eea;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        
        .ai-message {
            background: #f1f3f4;
            color: #333;
            margin-right: auto;
        }
        
        .input-area {
            padding: 20px;
            border-top: 1px solid #e9ecef;
            background: #fafafa;
        }
        
        .input-form {
            display: flex;
            gap: 10px;
            flex-direction: column;
        }
        
        .message-row {
            display: flex;
            gap: 10px;
            align-items: flex-end;
        }
        
        .attachment-area {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .image-preview {
            max-width: 100px;
            max-height: 100px;
            border-radius: 8px;
            border: 2px solid #e9ecef;
        }
        
        .image-preview-container {
            position: relative;
            display: inline-block;
        }
        
        .remove-image {
            position: absolute;
            top: -5px;
            right: -5px;
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .attach-button {
            background: #6c757d;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .attach-button:hover {
            background: #5a6268;
        }
        
        #messageInput {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            outline: none;
            font-size: 16px;
        }
        
        #messageInput:focus {
            border-color: #667eea;
        }
        
        #sendButton {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        
        #sendButton:hover {
            background: #5a6fd8;
        }
        
        #sendButton:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .typing-indicator {
            display: none;
            padding: 12px 16px;
            background: #f1f3f4;
            border-radius: 18px;
            margin-right: auto;
            max-width: 80px;
        }
        
        .typing-dots {
            display: flex;
            gap: 4px;
        }
        
        .typing-dots span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #999;
            animation: typing 1.5s infinite;
        }
        
        .typing-dots span:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dots span:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
            }
            30% {
                transform: translateY(-10px);
            }
        }
        
        .back-link {
            color: white;
            text-decoration: none;
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .back-link:hover {
            opacity: 1;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="security-badge">🔒 ACESSO AUTORIZADO</div>
        <h1>💬 IA Mamute Ultra-Segura</h1>
        <p>Converse com a IA mais segura e inteligente!</p>
        <a href="/" class="back-link">← Voltar ao início</a>
    </div>
    
    <div class="chat-container">
        <div class="messages" id="messages">
            <div class="message ai-message">
                🐘 Olá! Sou o Mamute, sua IA especialista em PostgreSQL e muito mais!<br>
                Como posso ajudar você hoje? 😊
            </div>
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
        
        <div class="input-area">
            <form class="input-form" id="chatForm">
                <div class="attachment-area" id="attachmentArea" style="display: none;">
                    <div id="imagePreview"></div>
                </div>
                <div class="message-row">
                    <button type="button" class="attach-button" id="attachButton">
                        📎 Anexar
                    </button>
                    <input 
                        type="text" 
                        id="messageInput" 
                        placeholder="Digite sua mensagem..." 
                        autocomplete="off"
                    >
                    <button type="submit" id="sendButton">Enviar</button>
                </div>
            </form>
            <input type="file" id="fileInput" accept="image/*" style="display: none;">
        </div>
    </div>
    
    <script>
        const messagesContainer = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const chatForm = document.getElementById('chatForm');
        const typingIndicator = document.getElementById('typingIndicator');
        
        let currentImage = null;
        
        function addMessage(content, isUser, imageUrl = null) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + (isUser ? 'user-message' : 'ai-message');
            
            let messageContent = '';
            if (imageUrl) {
                messageContent += `<img src="${imageUrl}" style="max-width: 200px; max-height: 200px; border-radius: 8px; margin-bottom: 10px; display: block;"><br>`;
            }
            messageContent += content;
            
            messageDiv.innerHTML = messageContent;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function showTyping() {
            typingIndicator.style.display = 'block';
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function hideTyping() {
            typingIndicator.style.display = 'none';
        }
        
        function setupImageUpload() {
            const attachButton = document.getElementById('attachButton');
            const fileInput = document.getElementById('fileInput');
            const attachmentArea = document.getElementById('attachmentArea');
            const imagePreview = document.getElementById('imagePreview');
            
            attachButton.addEventListener('click', () => {
                fileInput.click();
            });
            
            fileInput.addEventListener('change', async (e) => {
                const file = e.target.files[0];
                if (!file) return;
                
                // Verificar se é imagem
                if (!file.type.startsWith('image/')) {
                    alert('Por favor, selecione apenas arquivos de imagem.');
                    return;
                }
                
                // Verificar tamanho (10MB)
                if (file.size > 10 * 1024 * 1024) {
                    alert('Arquivo muito grande. Máximo 10MB.');
                    return;
                }
                
                try {
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    const response = await fetch('/upload-image', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        currentImage = data;
                        showImagePreview(data);
                    } else {
                        const error = await response.json();
                        alert('Erro ao fazer upload: ' + error.detail);
                    }
                } catch (error) {
                    alert('Erro ao fazer upload da imagem.');
                }
            });
        }
        
        function showImagePreview(imageData) {
            const attachmentArea = document.getElementById('attachmentArea');
            const imagePreview = document.getElementById('imagePreview');
            
            imagePreview.innerHTML = `
                <div class="image-preview-container">
                    <img src="data:${imageData.content_type};base64,${imageData.base64_data}" class="image-preview">
                    <button type="button" class="remove-image" onclick="removeImage()">&times;</button>
                </div>
                <small>${imageData.original_name} (${Math.round(imageData.size/1024)}KB)</small>
            `;
            
            attachmentArea.style.display = 'block';
        }
        
        function removeImage() {
            currentImage = null;
            document.getElementById('attachmentArea').style.display = 'none';
            document.getElementById('imagePreview').innerHTML = '';
            document.getElementById('fileInput').value = '';
        }
        
        async function sendMessage(message) {
            if (!message.trim() && !currentImage) return;
            
            // Adicionar mensagem do usuário (com imagem se houver)
            const imageUrl = currentImage ? currentImage.url : null;
            addMessage(message || '📷 Imagem enviada', true, imageUrl);
            
            // Preparar dados para envio
            const messageData = {
                message: message || '📷 Imagem enviada'
            };
            
            if (currentImage) {
                messageData.image_data = currentImage.base64_data;
                messageData.image_filename = currentImage.filename;
            }
            
            // Limpar input e desabilitar
            messageInput.value = '';
            removeImage();
            sendButton.disabled = true;
            messageInput.disabled = true;
            
            // Mostrar indicador de digitação
            showTyping();
            
            try {
                const response = await fetch('/chat/send', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(messageData)
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    addMessage(data.response, false);
                } else {
                    addMessage('❌ Erro: ' + (data.detail || 'Falha na comunicação'), false);
                }
            } catch (error) {
                addMessage('❌ Erro de conexão. Tente novamente.', false);
            } finally {
                // Esconder indicador e reabilitar input
                hideTyping();
                sendButton.disabled = false;
                messageInput.disabled = false;
                messageInput.focus();
            }
        }
        
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const message = messageInput.value;
            sendMessage(message);
        });
        
        // Configurar sistema de upload
        setupImageUpload();
        
        // Focar no input ao carregar
        messageInput.focus();
        
        // Adicionar mensagem de boas-vindas personalizada
        setTimeout(() => {
            addMessage('🔐 Sua conexão está segura e criptografada!<br>📊 Posso ajudar com SQL, PostgreSQL, programação e muito mais!<br>📎 <strong>Agora você também pode anexar imagens!</strong>', false);
        }, 1000);
    </script>
</body>
</html>
    """)

# ============================================================================
# PAINEL ADMINISTRATIVO
# ============================================================================

def get_admin_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if not security_manager.authenticate_admin(credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/admin")
async def admin_panel(admin: str = Depends(get_admin_auth)):
    pending = [req for req in security_manager.pending_requests.values() if req['status'] == 'pending']
    
    pending_html = ""
    for req in pending:
        pending_html += f"""
        <div style="border: 2px solid #ddd; padding: 20px; margin: 10px; border-radius: 10px;">
            <h3>🔔 Solicitação de {req['ip']}</h3>
            <p><strong>ID:</strong> {req['id']}</p>
            <p><strong>Hora:</strong> {req['timestamp'].strftime('%H:%M:%S')}</p>
            <p><strong>Dispositivo:</strong> {req['user_agent'][:100]}...</p>
            <div>
                <button onclick="handleRequest('{req['id']}', 'approve')" style="background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin: 5px;">
                    ✅ Aprovar
                </button>
                <button onclick="handleRequest('{req['id']}', 'deny')" style="background: #dc3545; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin: 5px;">
                    ❌ Negar
                </button>
            </div>
        </div>
        """
    
    if not pending_html:
        pending_html = "<p>📭 Nenhuma solicitação pendente</p>"
    
    return HTMLResponse(f"""
<!DOCTYPE html>
<html>
<head>
    <title>🔒 Painel Admin</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        h1 {{ color: #333; }}
    </style>
</head>
<body>
    <h1>🔒 Painel de Administração</h1>
    <h2>Solicitações Pendentes ({len(pending)})</h2>
    {pending_html}
    
    <script>
        async function handleRequest(requestId, action) {{
            try {{
                const response = await fetch('/admin/handle-request', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ request_id: requestId, action: action }})
                }});
                
                if (response.ok) {{
                    location.reload();
                }} else {{
                    alert('Erro ao processar solicitação');
                }}
            }} catch (error) {{
                alert('Erro de conexão');
            }}
        }}
    </script>
</body>
</html>
    """)

@app.post("/admin/handle-request")
async def handle_request(action_data: AdminAction, admin: str = Depends(get_admin_auth)):
    if action_data.action == "approve":
        session_id = security_manager.approve_request(action_data.request_id)
        if session_id:
            return {"status": "approved", "session_id": session_id}
    elif action_data.action == "deny":
        if security_manager.deny_request(action_data.request_id):
            return {"status": "denied"}
    
    raise HTTPException(status_code=404, detail="Solicitação não encontrada")

@app.get("/health")
async def health():
    return {"status": "ok", "secure": True}

@app.post("/chat/send")
async def chat_send(chat_data: ChatMessage, mamute_session: str = Cookie(None)):
    if not mamute_session:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    
    message = chat_data.message
    message_lower = message.lower()
    
    # Verificar se há imagem anexada
    has_image = chat_data.image_data is not None
    image_info = ""
    
    if has_image:
        # Processar imagem anexada
        try:
            # Decodificar base64 para analisar
            image_bytes = base64.b64decode(chat_data.image_data)
            image_size = len(image_bytes)
            image_info = f"\n\n📸 **Imagem anexada:** {chat_data.image_filename} ({round(image_size/1024)}KB)"
        except:
            image_info = "\n\n📸 **Imagem anexada** (formato não reconhecido)"
    
    # Obter horário para saudações contextuais
    hora_atual = datetime.now().hour
    if 5 <= hora_atual < 12:
        saudacao = "🌅 Bom dia"
    elif 12 <= hora_atual < 18:
        saudacao = "☀️ Boa tarde"  
    else:
        saudacao = "🌙 Boa noite"
    
    # =======================================================
    # PRIORIDADE 1: Tentar IA PRINCIPAL COMPLETA primeiro
    # =======================================================
    if ia_principal_disponivel and ia_instance:
        try:
            # Preparar contexto com imagem se houver
            chat_context = message
            if has_image:
                chat_context += f" [IMAGEM ANEXADA: {chat_data.image_filename}]"
            
            # Usar sistema de IA proativo e inteligente completo
            full_response = ia_instance.chat(chat_context, session_id="web_session")
            if full_response and len(full_response.strip()) > 10:
                # Adicionar saudação contextual se for cumprimento
                if any(word in message_lower for word in ["ola", "oi", "bom dia", "boa tarde"]):
                    full_response = f"{saudacao}! {full_response}"
                
                # Adicionar informação da imagem
                if has_image:
                    full_response += image_info
                
                return {
                    "response": full_response, 
                    "status": "success", 
                    "source": "ia_principal_completa",
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "has_image": has_image
                }
        except Exception as e:
            print(f"⚠️ Erro na IA principal: {e}")
            # Continuar para fallback
    
    # =======================================================
    # FALLBACK: Sistema de respostas especializadas  
    # =======================================================
    
    # Saudações contextuais
    if any(word in message_lower for word in ["ola", "oi", "bom dia", "boa tarde", "boa noite"]):
        response = f"""{saudacao}! 🐘 **Mamute IA Ultra-Segura ativada!**

🚀 **Suas especialidades principais:**
📊 PostgreSQL e SQL avançado
💻 Programação (26+ linguagens) 
🔍 Análise e otimização
🛠️ Criação de sistemas
📈 Dashboards e relatórios

💡 **Como posso ajudar você hoje?**
- Consultas SQL complexas
- Programação em qualquer linguagem
- Análise de banco de dados
- Otimização de performance
- Criação de sistemas

**Digite sua pergunta e eu darei uma resposta especializada!** ⚡"""
        
    # Comandos de banco de dados
    elif "comando" in message_lower and ("criar" in message_lower) and ("banco" in message_lower or "database" in message_lower):
        response = f"""🗄️ **COMANDOS PostgreSQL - CRIAÇÃO DE BANCO:**

**📊 1. Criar banco básico:**
```sql
CREATE DATABASE meu_banco;
```

**🔧 2. Criar com configurações completas:**
```sql
CREATE DATABASE empresa_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'pt_BR.UTF-8'
    LC_CTYPE = 'pt_BR.UTF-8'
    TABLESPACE = pg_default;
```

**🚀 3. Via linha de comando (Terminal):**
```bash
# Criar banco
createdb -U postgres -h localhost meu_banco

# Conectar ao banco
psql -U postgres -h localhost -d meu_banco
```

**📋 4. Verificar bancos existentes:**
```sql
-- Listar todos os bancos
\\l

-- Query SQL
SELECT datname, datowner, encoding 
FROM pg_database;
```

**⚡ 5. Criar tabelas após conectar:**
```sql
-- Conectar ao banco
\\c meu_banco;

-- Criar tabela exemplo
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Precisa de comandos mais específicos?** 🤔"""

    # Verificação de bancos existentes
    elif any(word in message_lower for word in ["existe", "tem", "há", "verificar"]) and ("banco" in message_lower or "database" in message_lower):
        response = f"""🔍 **VERIFICAÇÃO DE BANCOS DE DADOS - GUIA COMPLETO:**

**🐘 1. PostgreSQL:**
```bash
# Verificar versão
psql --version

# Verificar se está rodando
pg_isready

# Verificar status do serviço (Windows)
net start | findstr postgres

# Listar bancos disponíveis
psql -U postgres -l
```

**🐬 2. MySQL/MariaDB:**
```bash
# Verificar versão
mysql --version

# Verificar se está rodando
mysqladmin ping -u root -p

# Listar bancos
mysql -u root -p -e "SHOW DATABASES;"
```

**🟨 3. SQL Server:**
```bash
# Via SQLCMD
sqlcmd -S localhost -E -Q "SELECT name FROM sys.databases;"

# Verificar instâncias
sqlcmd -L
```

**🔧 4. Comandos universais (Windows):**
```cmd
# Verificar serviços ativos
services.msc

# Portas em uso
netstat -an | findstr :5432    (PostgreSQL)
netstat -an | findstr :3306    (MySQL)
netstat -an | findstr :1433    (SQL Server)
```

**📊 5. Script Python para verificar:**
```python
import psycopg2
try:
    conn = psycopg2.connect(
        host="localhost",
        database="postgres", 
        user="postgres",
        password="sua_senha"
    )
    print("✅ PostgreSQL conectado!")
except:
    print("❌ PostgreSQL não encontrado")
```

**Qual banco específico você quer verificar?** 💭"""

    # Comandos SQL específicos
    elif "sql" in message_lower or "postgres" in message_lower or "consulta" in message_lower:
        response = f"""🗄️ **ESPECIALISTA SQL/PostgreSQL ATIVADO!**

**💡 Posso ajudar com:**

**📊 CONSULTAS AVANÇADAS:**
```sql
-- JOINs complexos
-- Subconsultas (Subqueries)  
-- CTEs (Common Table Expressions)
-- Window Functions
-- Triggers e Procedures
```

**⚡ OTIMIZAÇÃO:**
```sql
-- Análise de planos: EXPLAIN ANALYZE
-- Criação de índices eficientes
-- Particionamento de tabelas
-- Tuning de queries lentas
```

**🔧 ADMINISTRAÇÃO:**
```sql
-- Backup e restore
-- Usuários e permissões
-- Configurações de performance
-- Monitoramento de conexões
```

**🛡️ SEGURANÇA:**
```sql
-- Row Level Security (RLS)
-- Roles e privilégios
-- Auditoria de comandos
-- Conexões seguras SSL
```

**🎯 EXEMPLOS RÁPIDOS:**
- "Como fazer JOIN de 3 tabelas"
- "Otimizar consulta lenta" 
- "Criar índice para performance"
- "Backup de banco específico"

**Qual área específica você precisa?** 🚀"""

    # Programação 
    elif "programacao" in message_lower or "programação" in message_lower or "codigo" in message_lower or "linguagem" in message_lower:
        response = f"""💻 **ESPECIALISTA EM PROGRAMAÇÃO - 26+ LINGUAGENS!**

**🔥 PRINCIPAIS ESPECIALIDADES:**

**🐍 PYTHON:**
- Django, Flask, FastAPI
- Data Science (Pandas, NumPy)
- Machine Learning (TensorFlow, PyTorch)
- Automação e Scripts

**☕ JAVA:**
- Spring Boot, Spring Framework
- Microserviços e APIs REST
- Sistemas enterprise
- Android Development

**🌐 JAVASCRIPT:**
- Node.js, React, Vue.js
- TypeScript, Express
- APIs modernas
- Frontend interativo

**⚙️ C/C++:**
- Performance crítica
- Sistemas embarcados
- Algoritmos otimizados
- Drivers e low-level

**🎯 OUTRAS ESPECIALIDADES:**
- **C#** (.NET Framework/Core)
- **Pascal** (Delphi, sistemas legados)  
- **Go** (Microserviços, concorrência)
- **Rust** (Segurança, performance)
- **PHP** (Laravel, WordPress)
- **Ruby** (Rails, scripting)

**💡 POSSO AJUDAR COM:**
✅ Algoritmos e estruturas de dados
✅ Design patterns avançados
✅ APIs REST e GraphQL
✅ Integração com bancos de dados
✅ Debugging e otimização
✅ Arquiteturas de software
✅ Code review e refatoração

**Qual linguagem ou projeto específico você tem?** 🚀"""

    # Dashboard e interfaces
    elif "dashboard" in message_lower or "interface" in message_lower or "web" in message_lower:
        response = f"""📊 **CRIADOR DE DASHBOARDS E INTERFACES WEB!**

**🖥️ POSSO CRIAR:**

**📈 DASHBOARDS INTERATIVOS:**
- Gráficos dinâmicos em tempo real
- KPIs e métricas importantes
- Filtros avançados e drill-down
- Relatórios automáticos

**🎨 TECNOLOGIAS FRONTEND:**
- **React** + Chart.js / D3.js
- **Vue.js** + Vuetify/Quasar
- **Angular** + Material Design
- **HTML5/CSS3** puro otimizado

**⚡ BACKEND PODEROSO:**
- **FastAPI** (Python) - Ultrarrápido
- **Django** - Framework completo
- **Node.js** + Express
- **Spring Boot** (Java)

**🔄 DADOS EM TEMPO REAL:**
- WebSockets para atualizações live
- Server-Sent Events (SSE)
- Conectores para PostgreSQL/MySQL
- APIs REST e GraphQL

**📊 VISUALIZAÇÕES:**
- Gráficos de linha, barras, pizza
- Mapas interativos (Leaflet/MapBox)
- Tabelas com paginação e filtros
- Calendários e cronogramas

**🛡️ SEGURANÇA:**
- Autenticação JWT
- Controle de acesso (RBAC)
- Conexões HTTPS/SSL
- Sessões seguras

**💡 EXEMPLOS DE DASHBOARDS:**
- Vendas e financeiro
- Monitoramento de sistemas
- Analytics de website
- Gestão de projetos
- IoT e sensores

**Que tipo de dashboard você quer criar?** 🎯"""

    # Ajuda geral
    elif "help" in message_lower or "ajuda" in message_lower:
        response = f"""🆘 **CENTRAL DE AJUDA - IA MAMUTE ULTRA-SEGURA**

**🔥 RECURSOS PRINCIPAIS:**

**🗄️ BANCO DE DADOS:**
- PostgreSQL (especialidade principal)
- MySQL, SQL Server, Oracle
- Consultas SQL complexas
- Otimização e performance
- Backup, restore, migrations

**💻 PROGRAMAÇÃO:**
- 26+ linguagens dominadas
- Algoritmos e estruturas de dados
- APIs REST, GraphQL, microserviços  
- Design patterns e arquiteturas
- Debugging e code review

**📊 ANÁLISE E DASHBOARDS:**
- Business Intelligence (BI)
- Visualizações interativas
- Relatórios automáticos
- KPIs e métricas
- Dashboards em tempo real

**🛠️ DESENVOLVIMENTO:**
- Sistemas web completos
- Mobile (Android/iOS)
- Desktop (Electron, Qt)
- Scripts e automação
- Integração de sistemas

**🔒 SEGURANÇA:**
- Autenticação e autorização
- Criptografia e SSL/TLS
- Auditoria e logs
- Compliance e LGPD
- Testes de penetração

**💬 COMANDOS ÚTEIS:**
- "verificar banco postgres"
- "criar comando SQL para..."
- "programação em Python para..."
- "criar dashboard de vendas"
- "otimizar consulta lenta"
- "configurar segurança em..."

**🎯 DICA PRO:** Seja específico! Quanto mais detalhes, melhor minha resposta.

**Em que posso ajudar agora?** 🚀"""

    # Resposta inteligente para outras perguntas
    else:
        response = f"""🤖 **ANALISANDO SUA SOLICITAÇÃO:**

"{message}"

**💭 Como especialista em tecnologia, posso ajudar com:**

**🗄️ BANCO DE DADOS:**
- PostgreSQL, MySQL, SQL Server
- Consultas SQL otimizadas
- Design de schemas
- Performance tuning

**💻 PROGRAMAÇÃO:**  
- Python, Java, JavaScript, C/C++
- Frameworks modernos
- APIs e microserviços
- Algoritmos avançados

**📊 ANÁLISE & DASHBOARDS:**
- Business Intelligence
- Visualizações interativas
- Relatórios automáticos
- KPIs e métricas

**🛠️ SOLUÇÕES PERSONALIZADAS:**
- Sistemas web completos
- Automação de processos
- Integração de sistemas
- Arquiteturas escaláveis

**💡 REFORMULE SUA PERGUNTA:**
Seja mais específico para uma resposta completa:

**✅ EXEMPLOS BONS:**
- "Como criar consulta SQL que junte 3 tabelas?"
- "Código Python para conectar PostgreSQL"
- "Dashboard em React para vendas"
- "Otimizar query que demora 30 segundos"

**❌ EVITAR:**
- Perguntas muito vagas
- Comandos sem contexto

**Pode reformular com mais detalhes?** 🎯"""

    return {
        "response": response, 
        "status": "success", 
        "source": "ia_especializada",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }

**3. 📋 Dentro do PostgreSQL:**
```sql
\\l                    -- Lista bancos
\\c nome_do_banco     -- Conecta ao banco
\\dt                   -- Lista tabelas
\\q                    -- Sair
```

**4. 🖥️ Verificar serviço (Windows):**
```cmd
sc query postgresql
net start postgresql
```

Quer que eu te ajude a conectar em algum banco específico? 🚀"""

    elif "sql" in message or "postgres" in message or "postgresql" in message:
        if "comando" in message or "query" in message:
            response = """📊 **Comandos PostgreSQL essenciais:**

**🏗️ Estrutura:**
```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    data_criacao TIMESTAMP DEFAULT NOW()
);
```

**📝 Inserir dados:**
```sql
INSERT INTO usuarios (nome, email) 
VALUES ('João Silva', 'joao@email.com');
```

**🔍 Consultar:**
```sql
SELECT * FROM usuarios WHERE nome LIKE '%João%';
```

**✏️ Atualizar:**
```sql
UPDATE usuarios SET email = 'novo@email.com' WHERE id = 1;
```

**🗑️ Deletar:**
```sql
DELETE FROM usuarios WHERE id = 1;
```

Precisa de alguma consulta específica? 🎯"""
        else:
            response = "🗄️ Especialista em PostgreSQL aqui! Posso ajudar com consultas, otimização, comandos específicos ou qualquer dúvida sobre bancos de dados. O que você precisa? 🚀"
            
    elif "programacao" in message or "programação" in message or "codigo" in message or "linguagem" in message:
        response = f"""💻 **Linguagens de programação que domino:**

🐍 **Python** - Análise de dados, web, automação
☕ **Java** - Aplicações enterprise, Spring Boot  
🌐 **JavaScript** - Frontend, Node.js, React
🔷 **C/C++** - Sistemas, performance crítica
📱 **Pascal** - Estruturas, algoritmos clássicos
🌟 **SQL** - Bancos de dados, consultas complexas

✨ **Também trabalho com:**
- 🚀 Framework web (Django, Flask, FastAPI)
- 📊 Análise de dados (Pandas, NumPy)
- 🤖 Machine Learning (Scikit-learn)
- 🔗 APIs REST e GraphQL

Qual linguagem ou projeto você quer desenvolver? 🎯"""

    elif "clima" in message or "tempo" in message:
        response = f"""🌤️ **Para dados meteorológicos com SQL:**

```sql
-- Exemplo de consulta clima
SELECT 
    cidade,
    temperatura,
    umidade,
    data_medicao
FROM dados_clima 
WHERE cidade = 'São Paulo'
    AND data_medicao >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY data_medicao DESC;
```

🌡️ Posso ajudar a criar consultas para análise de dados climáticos em bancos de dados! 📊"""

    elif "ajuda" in message or "help" in message:
        response = f"""🆘 **{saudacao}! Sou sua IA especialista completa!**

🎯 **Principais especialidades:**
- 🗄️ **PostgreSQL/SQL**: Consultas, otimização, comandos
- 💻 **Programação**: Python, Java, C, JavaScript, Pascal
- 📊 **Análise de dados**: Pandas, relatórios, dashboards
- 🚀 **Web**: APIs, FastAPI, frameworks
- 🔧 **DevOps**: Comandos, automação, scripts

💡 **Exemplos do que posso fazer:**
- Criar comandos SQL específicos
- Resolver problemas de programação  
- Otimizar consultas de banco
- Explicar conceitos técnicos
- Gerar código funcional

🤔 **Me diga especificamente o que precisa e vou elaborar uma solução completa!**"""

    elif "obrigado" in message or "valeu" in message or "brigado" in message:
        response = f"😊 De nada! Foi um prazer ajudar! Estou sempre aqui quando precisar. {saudacao} e sucesso! 🚀"
        
    elif "tchau" in message or "bye" in message or "até" in message:
        response = f"👋 {saudacao} e até mais! Foi ótimo conversar com você. Volte sempre que precisar de ajuda! 🐘✨"
        
    elif "seguranca" in message or "segurança" in message:
        response = """🔒 **Sistema Ultra-Seguro Ativo!**

✅ **Proteções implementadas:**
- 🔐 Autorização manual obrigatória
- 🌐 Conexão HTTPS criptografada (ngrok)
- 🛡️ Bloqueio automático de IPs suspeitos
- 📝 Logs detalhados de todos acessos
- ⏰ Sessões temporárias (1 hora)
- 🔍 Análise de risco por solicitação

🎯 **Apenas usuários aprovados manualmente podem acessar esta IA!**

Sua conexão está totalmente protegida! 🛡️"""

    elif len(message.strip()) < 3:
        response = f"🤔 Posso ajudar você! Digite sua dúvida sobre PostgreSQL, programação ou qualquer coisa que precisar. 💻"
        
    else:
        # Resposta inteligente personalizada
        response = f"""🤔 **Interessante pergunta sobre: "{chat_data.message}"**

💡 **Como especialista completo, posso ajudar com:**

🗄️ **PostgreSQL**: Comandos, consultas, otimização
💻 **Programação**: Códigos, algoritmos, debugging  
📊 **Dados**: Análises, relatórios, visualizações
🔧 **DevOps**: Automação, scripts, deploy
🌐 **Web**: APIs, frontend, backend

🎯 **Para dar uma resposta mais específica, me diga:**
- Qual tecnologia está usando?
- Que tipo de resultado espera?
- Tem algum erro ou problema específico?

Assim posso elaborar uma solução completa e detalhada! 🚀"""

    # Adicionar informação da imagem se houver
    if has_image:
        response += image_info
    
    return {
        "response": response, 
        "status": "success", 
        "source": "ia_melhorada",
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "has_image": has_image
    }

if __name__ == "__main__":
    print("""
🔒 IA MAMUTE ULTRA-SEGURA (VERSÃO CORRIGIDA)
============================================

🌐 Acesso: /request-access
🔐 Admin: /admin (admin/mamute2026)

Agora SEM loops de redirecionamento!
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)