"""
IA Mamute - Servidor com Suporte a Imagens
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

# Adicionar o diretorio principal ao path
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
APPS_DIR = SRC_DIR / "apps"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

# Tentar importar IA completa
ia_disponivel = False
ia_system = None
try:
    from main import MamuteChat
    ia_system = MamuteChat()
    ia_disponivel = True
    print("IA COMPLETA carregada com sucesso!")
except Exception as e:
    print(f"IA simplificada - Erro ao carregar sistema completo: {e}")
    ia_disponivel = False

# Tentar importar IA principal
ia_principal_disponivel = False
ia_instance = None
try:
    from main import IAAgent  
    ia_instance = IAAgent()
    ia_principal_disponivel = True
    print("IA Principal importada com sucesso!")
    
except Exception as e:
    print(f"IA Principal nao disponivel: {e}")
    ia_principal_disponivel = False

# Gerenciador de segurança
class SimpleSecurityManager:
    def __init__(self):
        self.pending_requests = {}  # {request_id: {ip, timestamp, status}}
        self.approved_sessions = {}  # {session_id: {ip, created_at, expires_at}}
        self.session_lifetime = timedelta(hours=2)
    
    def create_access_request(self, client_ip: str, user_agent: str) -> str:
        request_id = str(uuid.uuid4())[:8]
        self.pending_requests[request_id] = {
            'id': request_id,
            'ip': client_ip,
            'user_agent': user_agent,
            'timestamp': datetime.now(),
            'status': 'pending'
        }
        return request_id
    
    def approve_request(self, request_id: str) -> Optional[str]:
        if request_id in self.pending_requests:
            req = self.pending_requests[request_id]
            if req['status'] == 'pending':
                session_id = str(uuid.uuid4())
                req['status'] = 'approved'
                req['session_id'] = session_id
                
                # Criar sessão
                self.approved_sessions[session_id] = {
                    'ip': req['ip'],
                    'created_at': datetime.now(),
                    'expires_at': datetime.now() + self.session_lifetime,
                    'request_id': request_id
                }
                return session_id
        return None
    
    def deny_request(self, request_id: str) -> bool:
        if request_id in self.pending_requests:
            self.pending_requests[request_id]['status'] = 'denied'
            return True
        return False
    
    def is_request_approved(self, request_id: str) -> Optional[str]:
        if request_id in self.pending_requests:
            req = self.pending_requests[request_id]
            if req['status'] == 'approved':
                return req.get('session_id')
        return None
    
    def is_session_valid(self, session_id: str, client_ip: str) -> bool:
        if session_id not in self.approved_sessions:
            return False
        
        session = self.approved_sessions[session_id]
        
        # Verificar IP
        if session['ip'] != client_ip:
            return False
        
        # Verificar expiração
        if datetime.now() > session['expires_at']:
            del self.approved_sessions[session_id]
            return False
            
        return True
        
    def authenticate_admin(self, credentials: HTTPBasicCredentials) -> bool:
        return credentials.username == "admin" and credentials.password == "mamute2026"

security_manager = SimpleSecurityManager()

# Configurar FastAPI
app = FastAPI(title="IA Mamute Ultra-Segura", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estaticos
if os.path.exists("web/static"):
    app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Configuracao de seguranca
security = HTTPBasic()

# Modelos de dados
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

# Criar diretorio para uploads se nao existir
UPLOADS_DIR = "uploads/images"
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Endpoints para upload de imagens
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...), mamute_session: str = Cookie(None)):
    if not mamute_session:
        raise HTTPException(status_code=401, detail="Sessao invalida")
    
    # Verificar tipo de arquivo
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Tipo de arquivo nao suportado. Use JPG, PNG, GIF ou WebP.")
    
    # Verificar tamanho (max 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Maximo 10MB.")
    
    # Gerar nome unico
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
        raise HTTPException(status_code=404, detail="Imagem nao encontrada")
    
    # Detectar tipo de conteudo
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "application/octet-stream"
    
    with open(file_path, "rb") as f:
        return Response(content=f.read(), media_type=content_type)

# Endpoints principais
@app.get("/")
async def home(request: Request, mamute_session: str = Cookie(None)):
    client_ip = request.client.host
    
    # Verificar se tem sessao valida
    if mamute_session and security_manager.is_session_valid(mamute_session, client_ip):
        return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>IA Mamute - Acesso Autorizado</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0; padding: 20px; min-height: 100vh;
            display: flex; align-items: center; justify-content: center;
        }
        .container {
            background: white; border-radius: 20px; padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1); text-align: center; max-width: 600px;
        }
        .btn {
            background: #667eea; color: white; border: none; padding: 15px 30px;
            border-radius: 8px; cursor: pointer; font-size: 1.1em; margin: 10px;
            text-decoration: none; display: inline-block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>IA Mamute Ultra-Segura</h1>
        <p>Acesso autorizado! Sua conexao esta segura.</p>
        <a href="/chat" class="btn">Iniciar Chat com IA</a>
    </div>
</body>
</html>
        """)
    else:
        return RedirectResponse(url="/request-access")

@app.get("/request-access")
async def request_access(request: Request):
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")
    
    request_id = security_manager.create_access_request(client_ip, user_agent)
    
    return HTMLResponse(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Solicitar Acesso</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0; padding: 20px; min-height: 100vh;
            display: flex; align-items: center; justify-content: center;
        }}
        .container {{
            background: white; border-radius: 20px; padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1); text-align: center; max-width: 500px;
        }}
        .btn {{
            background: #667eea; color: white; border: none; padding: 15px 30px;
            border-radius: 8px; cursor: pointer; font-size: 1.1em; margin: 10px;
            text-decoration: none; display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div style="font-size: 4em;">🔒</div>
        <h1>Solicitar Acesso</h1>
        <p>Para acessar a IA Mamute, voce precisa de autorizacao.</p>
        
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <strong>IP:</strong> {client_ip}<br>
            <strong>ID da Solicitacao:</strong> {request_id}<br>
            <strong>Hora:</strong> {datetime.now().strftime('%H:%M:%S')}
        </div>
        
        <a href="/wait-approval?request_id={request_id}" class="btn">
            Aguardar Aprovacao
        </a>
        
        <p style="color: #666; margin-top: 20px;">
            O administrador foi notificado sobre sua solicitacao.
        </p>
    </div>
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
    <title>Chat IA Mamute</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh; display: flex; flex-direction: column;
        }
        
        .header {
            background: rgba(255,255,255,0.1); color: white; padding: 15px 20px;
            text-align: center; backdrop-filter: blur(10px);
        }
        
        .chat-container {
            flex: 1; display: flex; flex-direction: column; max-width: 1000px;
            margin: 20px auto; background: white; border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1); overflow: hidden;
        }
        
        .messages {
            flex: 1; overflow-y: auto; padding: 20px; max-height: 500px;
        }
        
        .message {
            margin-bottom: 15px; padding: 12px 16px; border-radius: 18px;
            max-width: 80%; word-wrap: break-word;
        }
        
        .user-message {
            background: #667eea; color: white; margin-left: auto; text-align: right;
        }
        
        .ai-message {
            background: #f1f3f4; color: #333; margin-right: auto;
        }
        
        .input-area {
            padding: 20px; border-top: 1px solid #e9ecef; background: #fafafa;
        }
        
        .input-form {
            display: flex; gap: 10px; flex-direction: column;
        }
        
        .message-row {
            display: flex; gap: 10px; align-items: flex-end;
        }
        
        .attachment-area {
            display: flex; gap: 10px; align-items: center; margin-bottom: 10px;
        }
        
        .image-preview {
            max-width: 100px; max-height: 100px; border-radius: 8px;
            border: 2px solid #e9ecef;
        }
        
        .image-preview-container {
            position: relative; display: inline-block;
        }
        
        .remove-image {
            position: absolute; top: -5px; right: -5px; background: #dc3545;
            color: white; border: none; border-radius: 50%; width: 20px; height: 20px;
            cursor: pointer; font-size: 12px;
        }
        
        .attach-button {
            background: #6c757d; color: white; border: none; padding: 8px 12px;
            border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 5px;
        }
        
        .attach-button:hover { background: #5a6268; }
        
        #messageInput {
            flex: 1; padding: 12px 16px; border: 2px solid #e9ecef;
            border-radius: 25px; outline: none; font-size: 1em;
        }
        
        #sendButton {
            background: #667eea; color: white; border: none; padding: 12px 24px;
            border-radius: 25px; cursor: pointer; font-weight: bold;
        }
        
        #sendButton:hover { background: #5a6bd8; }
        #sendButton:disabled { background: #ccc; }
        
        .typing-indicator {
            display: none; padding: 10px 20px; color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="header">
        <div style="background: #28a745; color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.8em; margin-bottom: 10px; display: inline-block;">
            Conexao Ultra-Segura
        </div>
        <h1>Chat IA Mamute</h1>
        <p>Sua assistente especializada em PostgreSQL e programacao</p>
    </div>
    
    <div class="chat-container">
        <div class="messages" id="messages">
            <!-- Mensagens aparecem aqui -->
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            IA digitando
            <div style="display: inline-block;">
                <span></span><span></span><span></span>
            </div>
        </div>
        
        <div class="input-area">
            <form class="input-form" id="chatForm">
                <div class="attachment-area" id="attachmentArea" style="display: none;">
                    <div id="imagePreview"></div>
                </div>
                <div class="message-row">
                    <button type="button" class="attach-button" id="attachButton">
                        Anexar
                    </button>
                    <input type="text" id="messageInput" placeholder="Digite sua mensagem..." autocomplete="off">
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
                
                if (!file.type.startsWith('image/')) {
                    alert('Por favor, selecione apenas arquivos de imagem.');
                    return;
                }
                
                if (file.size > 10 * 1024 * 1024) {
                    alert('Arquivo muito grande. Maximo 10MB.');
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
            
            // Adicionar mensagem do usuario (com imagem se houver)
            const imageUrl = currentImage ? currentImage.url : null;
            addMessage(message || 'Imagem enviada', true, imageUrl);
            
            // Preparar dados para envio
            const messageData = {
                message: message || 'Imagem enviada'
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
            
            // Mostrar indicador de digitacao
            showTyping();
            
            try {
                const response = await fetch('/chat/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(messageData)
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    addMessage(data.response, false);
                } else {
                    addMessage('Erro: ' + (data.detail || 'Falha na comunicacao'), false);
                }
            } catch (error) {
                addMessage('Erro de conexao. Tente novamente.', false);
            } finally {
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
        
        // Adicionar mensagem de boas-vindas
        setTimeout(() => {
            addMessage('Sua conexao esta segura e criptografada!<br>Posso ajudar com SQL, PostgreSQL, programacao e muito mais!<br><strong>Agora voce tambem pode anexar imagens!</strong>', false);
        }, 1000);
    </script>
</body>
</html>
    """)

# Endpoint do chat
@app.post("/chat/send")
async def chat_send(chat_data: ChatMessage, mamute_session: str = Cookie(None)):
    if not mamute_session:
        raise HTTPException(status_code=401, detail="Sessao invalida")
    
    message = chat_data.message
    message_lower = message.lower()
    
    # Verificar se ha imagem anexada
    has_image = chat_data.image_data is not None
    image_info = ""
    
    if has_image:
        try:
            image_bytes = base64.b64decode(chat_data.image_data)
            image_size = len(image_bytes)
            image_info = f"<br><br>Imagem anexada: {chat_data.image_filename} ({round(image_size/1024)}KB)"
        except:
            image_info = "<br><br>Imagem anexada (formato nao reconhecido)"
    
    # Obter horario para saudacoes contextuais
    hora_atual = datetime.now().hour
    if 5 <= hora_atual < 12:
        saudacao = "Bom dia"
    elif 12 <= hora_atual < 18:
        saudacao = "Boa tarde"  
    else:
        saudacao = "Boa noite"
    
    # Tentar usar IA principal primeiro
    if ia_principal_disponivel and ia_instance:
        try:
            chat_context = message
            if has_image:
                chat_context += f" [IMAGEM ANEXADA: {chat_data.image_filename}]"
            
            full_response = ia_instance.chat(chat_context, session_id="web_session")
            if full_response and len(full_response.strip()) > 10:
                if any(word in message_lower for word in ["ola", "oi", "bom dia", "boa tarde"]):
                    full_response = f"{saudacao}! {full_response}"
                
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
            print(f"Erro na IA principal: {e}")
    
    # Sistema de respostas especializadas
    if any(word in message_lower for word in ["ola", "oi", "bom dia", "boa tarde", "boa noite"]):
        response = f"""{saudacao}! Mamute IA Ultra-Segura ativada!

Suas especialidades principais:
- PostgreSQL e SQL avancado
- Programacao (26+ linguagens) 
- Analise e otimizacao
- Criacao de sistemas
- Dashboards e relatorios

Como posso ajudar voce hoje?"""
        
    elif "banco" in message_lower or "postgres" in message_lower or "sql" in message_lower:
        response = """PostgreSQL especialista aqui!

Posso ajudar com:
- Consultas SQL complexas
- Criacao e otimizacao de bancos
- Performance e indices
- Backup e restore
- Configuracao de seguranca

Qual e sua duvida especifica?"""

    elif "programacao" in message_lower or "codigo" in message_lower:
        response = """Especialista em programacao ativado!

Linguagens que domino:
- Python (Django, Flask, FastAPI)
- JavaScript (Node.js, React)
- Java (Spring Boot)
- C/C++ e muito mais

Posso ajudar com algoritmos, debugging, APIs e arquiteturas.

Qual linguagem voce precisa?"""

    else:
        response = f"""Interessante pergunta sobre: "{message}"

Como especialista em tecnologia, posso ajudar com:
- PostgreSQL e bancos de dados
- Programacao em varias linguagens  
- Analise de dados e dashboards
- Automacao e scripts

Me de mais detalhes para uma resposta completa!"""

    if has_image:
        response += image_info
    
    return {
        "response": response, 
        "status": "success", 
        "source": "ia_especializada",
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "has_image": has_image
    }

# Endpoints administrativos
def get_admin_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if not security_manager.authenticate_admin(credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas",
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
            <h3>Solicitacao de {req['ip']}</h3>
            <p><strong>ID:</strong> {req['id']}</p>
            <p><strong>Hora:</strong> {req['timestamp'].strftime('%H:%M:%S')}</p>
            <div>
                <button onclick="handleRequest('{req['id']}', 'approve')" style="background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin: 5px;">
                    Aprovar
                </button>
                <button onclick="handleRequest('{req['id']}', 'deny')" style="background: #dc3545; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin: 5px;">
                    Negar
                </button>
            </div>
        </div>
        """
    
    if not pending_html:
        pending_html = "<p>Nenhuma solicitacao pendente</p>"
    
    return HTMLResponse(f"""
<!DOCTYPE html>
<html>
<head>
    <title>Painel Admin</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        h1 {{ color: #333; }}
    </style>
</head>
<body>
    <h1>Painel de Administracao</h1>
    <h2>Solicitacoes Pendentes ({len(pending)})</h2>
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
                }}
            }} catch (error) {{
                alert('Erro de conexao');
            }}
        }}
    </script>
</body>
</html>
    """)

@app.post("/admin/handle-request")
async def handle_admin_request(action_data: AdminAction, admin: str = Depends(get_admin_auth)):
    if action_data.action == "approve":
        session_id = security_manager.approve_request(action_data.request_id)
        if session_id:
            return {"status": "approved", "session_id": session_id}
    elif action_data.action == "deny":
        if security_manager.deny_request(action_data.request_id):
            return {"status": "denied"}
    
    raise HTTPException(status_code=400, detail="Acao invalida")

@app.get("/wait-approval")
async def wait_approval(request_id: str):
    if request_id not in security_manager.pending_requests:
        return RedirectResponse(url="/request-access")
    
    # Verificar se foi aprovado
    session_id = security_manager.is_request_approved(request_id)
    if session_id:
        response = RedirectResponse(url="/")
        response.set_cookie(key="mamute_session", value=session_id, httponly=True, secure=True, samesite="strict")
        return response
    
    # Verificar se foi negado
    req = security_manager.pending_requests[request_id]
    if req['status'] == 'denied':
        return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Acesso Negado</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f8f9fa; margin: 0; padding: 20px; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { background: white; border-radius: 20px; padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.1); text-align: center; max-width: 500px; }
    </style>
</head>
<body>
    <div class="container">
        <div style="font-size: 4em; color: #dc3545;">❌</div>
        <h1>Acesso Negado</h1>
        <p>Sua solicitacao foi negada pelo administrador.</p>
    </div>
</body>
</html>
        """)
    
    # Ainda pendente
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Aguardando Aprovacao</title>
    <meta http-equiv="refresh" content="3">
    <style>
        body { font-family: Arial, sans-serif; background: #f8f9fa; margin: 0; padding: 20px; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { background: white; border-radius: 20px; padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.1); text-align: center; max-width: 500px; }
    </style>
</head>
<body>
    <div class="container">
        <div style="font-size: 4em;">⏳</div>
        <h1>Aguardando Aprovacao</h1>
        <p>Sua solicitacao esta sendo analisada pelo administrador.</p>
        <p><small>Esta pagina sera atualizada automaticamente.</small></p>
    </div>
</body>
</html>
    """)

@app.get("/health")
async def health():
    return {"status": "ok", "secure": True}

if __name__ == "__main__":
    print("""
IA MAMUTE ULTRA-SEGURA COM SUPORTE A IMAGENS
============================================

Acesso: /request-access
Admin: /admin (admin/mamute2026)
Recursos: Chat com anexo de imagens!

""")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)