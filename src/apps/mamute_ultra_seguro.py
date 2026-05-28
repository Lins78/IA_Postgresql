"""
IA Mamute - Versão Ultra-Segura com Autorização Manual
Cada acesso deve ser aprovado manualmente pelo administrador
"""
from fastapi import FastAPI, HTTPException, Request, Depends, Cookie, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
import time
import json
import uvicorn
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

# Importar sistema de segurança
from sistema_seguranca import security_manager, require_authorization, AdminAction, AccessRequest, security

# Importar IA
try:
    from main import IAPostgreSQL
    from src.utils.logger import setup_logger
    ia_disponivel = True
except:
    ia_disponivel = False

app = FastAPI(title="🔒 IA Mamute Ultra-Segura", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de segurança global
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    try:
        await require_authorization(request)
        response = await call_next(request)
        return response
    except HTTPException as e:
        if e.status_code == 401:
            detail = e.detail
            if isinstance(detail, dict) and "redirect" in detail:
                return RedirectResponse(url=detail["redirect"], status_code=302)
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        )

# Servir arquivos estáticos
if os.path.exists("web/static"):
    app.mount("/static", StaticFiles(directory="web/static"), name="static")

# ============================================================================
# ENDPOINTS PÚBLICOS (Autorização e Aguardo)
# ============================================================================

@app.get("/request-access")
async def request_access(request: Request):
    """Solicitar acesso à IA"""
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    
    try:
        request_id = security_manager.create_access_request(client_ip, user_agent, "/")
        return HTMLResponse(f"""
<!DOCTYPE html>
<html>
<head>
    <title>🔒 Acesso Solicitado - IA Mamute</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
            width: 100%;
        }}
        .icon {{
            font-size: 4em;
            margin-bottom: 20px;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        .info {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .status {{
            background: #fff3cd;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #ffeaa7;
            margin: 20px 0;
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
        .btn:hover {{
            background: #5a6fd8;
        }}
        .loading {{
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 10px;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">🔒</div>
        <h1>Acesso Solicitado!</h1>
        <p class="subtitle">Sua solicitação foi enviada ao administrador</p>
        
        <div class="info">
            <strong>📍 IP:</strong> {client_ip}<br>
            <strong>🌍 Local:</strong> {security_manager.get_location(client_ip)}<br>
            <strong>🆔 ID:</strong> {request_id}<br>
            <strong>⏰ Hora:</strong> {datetime.now().strftime('%H:%M:%S')}
        </div>
        
        <div class="status">
            <div class="loading"></div>
            <strong>Aguardando autorização do administrador...</strong>
        </div>
        
        <p>O administrador foi notificado e irá revisar sua solicitação.</p>
        
        <a href="/wait-approval?request_id={request_id}" class="btn">
            📊 Verificar Status
        </a>
        
        <br><br>
        <small style="color: #666;">
            Esta IA está em desenvolvimento e requer aprovação manual para acesso.
        </small>
    </div>
    
    <script>
        // Auto-atualizar a cada 5 segundos
        setTimeout(() => {{
            window.location.href = '/wait-approval?request_id={request_id}';
        }}, 5000);
    </script>
</body>
</html>
        """)
    except HTTPException as e:
        if "bloqueado" in str(e.detail):
            return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>🚫 Acesso Bloqueado</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #ff6b6b; color: white; }
        .container { background: rgba(0,0,0,0.1); padding: 40px; border-radius: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚫 Acesso Bloqueado</h1>
        <p>Seu IP foi bloqueado por tentativas de acesso não autorizadas.</p>
        <p>Entre em contato com o administrador se precisar de acesso.</p>
    </div>
</body>
</html>
            """)

@app.get("/wait-approval")
async def wait_approval(request_id: str):
    """Página de espera por aprovação"""
    if request_id not in security_manager.pending_requests:
        return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>❓ Solicitação não encontrada</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
    </style>
</head>
<body>
    <h1>❓ Solicitação não encontrada</h1>
    <p><a href="/request-access">Solicitar novo acesso</a></p>
</body>
</html>
        """)
    
    req = security_manager.pending_requests[request_id]
    
    if req['status'] == 'approved':
        session_id = req.get('session_id')
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie("mamute_session", session_id, max_age=3600)  # 1 hora
        return response
    elif req['status'] == 'denied':
        return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>❌ Acesso Negado</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #ff6b6b; color: white; }
        .container { background: rgba(0,0,0,0.1); padding: 40px; border-radius: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>❌ Acesso Negado</h1>
        <p>Sua solicitação de acesso foi negada pelo administrador.</p>
        <p>Seu IP foi bloqueado por segurança.</p>
    </div>
</body>
</html>
        """)
    
    # Ainda pendente - mostrar status
    return HTMLResponse(f"""
<!DOCTYPE html>
<html>
<head>
    <title>⏳ Aguardando Aprovação - IA Mamute</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="3">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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
            width: 100%;
        }}
        .icon {{
            font-size: 4em;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.1); }}
            100% {{ transform: scale(1); }}
        }}
        .status {{
            background: #fff3cd;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #ffeaa7;
            margin: 20px 0;
            font-weight: bold;
        }}
        .info {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: left;
        }}
        .waiting-time {{
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">⏳</div>
        <h1>Aguardando Aprovação</h1>
        
        <div class="status">
            🔍 Sua solicitação está sendo analisada...
        </div>
        
        <div class="info">
            <strong>📊 Status:</strong> {req['status'].title()}<br>
            <strong>⏰ Solicitado em:</strong> {req['timestamp'].strftime('%H:%M:%S')}<br>
            <strong>🆔 ID:</strong> {request_id}<br>
            <strong>🌍 Localização:</strong> {req['location']}<br>
            <strong>⚠️ Nível de Risco:</strong> {req['risk_level']}
        </div>
        
        <div class="waiting-time">
            Tempo de espera: {(datetime.now() - req['timestamp']).seconds}s
        </div>
        
        <p>A página será atualizada automaticamente a cada 3 segundos.</p>
        
        <small style="color: #666;">
            O administrador recebeu uma notificação sobre sua solicitação.
        </small>
    </div>
</body>
</html>
    """)

# ============================================================================
# PAINEL ADMINISTRATIVO
# ============================================================================

def get_admin_auth(credentials: HTTPBasicCredentials = Depends(security)):
    """Autenticação do administrador"""
    if not security_manager.authenticate_admin(credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/admin")
async def admin_panel(admin: str = Depends(get_admin_auth)):
    """Painel administrativo"""
    pending = [req for req in security_manager.pending_requests.values() if req['status'] == 'pending']
    recent_logs = security_manager.access_logs[-10:]  # Últimos 10 logs
    
    pending_html = ""
    for req in pending:
        pending_html += f"""
        <div class="request-card" data-id="{req['id']}">
            <h3>🔔 Nova Solicitação</h3>
            <div class="request-info">
                <p><strong>📍 IP:</strong> {req['ip']}</p>
                <p><strong>🌍 Local:</strong> {req['location']}</p>
                <p><strong>⚠️ Risco:</strong> {req['risk_level']}</p>
                <p><strong>🖥️ Dispositivo:</strong> {req['user_agent'][:100]}...</p>
                <p><strong>📄 Página:</strong> {req['path']}</p>
                <p><strong>⏰ Hora:</strong> {req['timestamp'].strftime('%H:%M:%S')}</p>
            </div>
            <div class="request-actions">
                <button class="btn-approve" onclick="handleRequest('{req['id']}', 'approve')">
                    ✅ Aprovar
                </button>
                <button class="btn-deny" onclick="handleRequest('{req['id']}', 'deny')">
                    ❌ Negar & Bloquear
                </button>
            </div>
        </div>
        """
    
    if not pending_html:
        pending_html = "<div class='no-requests'>📭 Nenhuma solicitação pendente</div>"
    
    logs_html = ""
    for log in reversed(recent_logs):
        icon = {"access_requested": "🔔", "access_approved": "✅", "access_denied": "❌"}.get(log['action'], "📝")
        logs_html += f"""
        <div class="log-entry">
            <span class="log-time">{log['timestamp'].strftime('%H:%M:%S')}</span>
            <span class="log-icon">{icon}</span>
            <span class="log-ip">{log['ip']}</span>
            <span class="log-action">{log['action']}</span>
        </div>
        """
    
    return HTMLResponse(f"""
<!DOCTYPE html>
<html>
<head>
    <title>🔒 Admin - IA Mamute Ultra-Segura</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="5">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .header {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .main-content {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }}
        
        .section {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .section-header {{
            background: #667eea;
            color: white;
            padding: 20px;
            font-size: 1.2em;
            font-weight: bold;
        }}
        
        .section-content {{
            padding: 20px;
            max-height: 600px;
            overflow-y: auto;
        }}
        
        .request-card {{
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }}
        
        .request-card:hover {{
            border-color: #667eea;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
        }}
        
        .request-info {{
            margin: 15px 0;
            line-height: 1.8;
        }}
        
        .request-actions {{
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }}
        
        .btn-approve {{
            background: #28a745;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            flex: 1;
        }}
        
        .btn-approve:hover {{
            background: #218838;
        }}
        
        .btn-deny {{
            background: #dc3545;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            flex: 1;
        }}
        
        .btn-deny:hover {{
            background: #c82333;
        }}
        
        .no-requests {{
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 40px;
        }}
        
        .log-entry {{
            display: grid;
            grid-template-columns: 80px 40px 120px 1fr;
            gap: 10px;
            padding: 10px;
            border-bottom: 1px solid #e9ecef;
            font-size: 0.9em;
        }}
        
        .log-time {{
            color: #666;
        }}
        
        .log-ip {{
            font-family: monospace;
            font-weight: bold;
        }}
        
        .alert {{
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            z-index: 1000;
        }}
        
        .alert-success {{
            background: #28a745;
        }}
        
        .alert-error {{
            background: #dc3545;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 IA Mamute - Painel de Segurança Ultra</h1>
        <p>Controle total sobre o acesso à sua IA</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{len(pending)}</div>
            <div>Solicitações Pendentes</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(security_manager.approved_sessions)}</div>
            <div>Sessões Ativas</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(security_manager.blocked_ips)}</div>
            <div>IPs Bloqueados</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(security_manager.access_logs)}</div>
            <div>Total de Logs</div>
        </div>
    </div>
    
    <div class="main-content">
        <div class="section">
            <div class="section-header">
                🔔 Solicitações de Acesso ({len(pending)} pendentes)
            </div>
            <div class="section-content">
                {pending_html}
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">
                📋 Logs Recentes
            </div>
            <div class="section-content">
                {logs_html}
            </div>
        </div>
    </div>
    
    <script>
        async function handleRequest(requestId, action) {{
            try {{
                const response = await fetch('/admin/handle-request', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        request_id: requestId,
                        action: action
                    }})
                }});
                
                const result = await response.json();
                
                if (response.ok) {{
                    showAlert(action === 'approve' ? 'Acesso aprovado!' : 'Acesso negado!', 'success');
                    // Remover o card da interface
                    document.querySelector(`[data-id="${{requestId}}"]`).remove();
                }} else {{
                    showAlert('Erro: ' + result.detail, 'error');
                }}
            }} catch (error) {{
                showAlert('Erro de conexão', 'error');
            }}
        }}
        
        function showAlert(message, type) {{
            const alert = document.createElement('div');
            alert.className = `alert alert-${{type}}`;
            alert.textContent = message;
            document.body.appendChild(alert);
            
            setTimeout(() => {{
                alert.remove();
            }}, 3000);
        }}
        
        // Auto-refresh para capturar novas solicitações
        console.log('🔒 Painel de Segurança Ativo - Monitorando solicitações...');
    </script>
</body>
</html>
    """)

@app.post("/admin/handle-request")
async def handle_request(action_data: AdminAction, admin: str = Depends(get_admin_auth)):
    """Aprovar ou negar solicitação"""
    request_id = action_data.request_id
    action = action_data.action
    
    if action == "approve":
        session_id = security_manager.approve_request(request_id)
        if session_id:
            return {"status": "approved", "session_id": session_id}
        else:
            raise HTTPException(status_code=404, detail="Solicitação não encontrada")
            
    elif action == "deny":
        if security_manager.deny_request(request_id):
            return {"status": "denied"}
        else:
            raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    
    else:
        raise HTTPException(status_code=400, detail="Ação inválida")

# ============================================================================
# ENDPOINTS DA IA (Protegidos)
# ============================================================================

@app.get("/")
async def home():
    """Página inicial da IA (protegida)"""
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
        .btn:hover { background: #f8f9fa; }
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

@app.get("/chat")
async def chat_interface():
    """Interface de chat (protegida)"""
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>💬 Chat IA Mamute</title>
    <meta charset="utf-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0;
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .chat-container { 
            max-width: 800px;
            margin: 0 auto;
            background: white; 
            border-radius: 20px; 
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: #333;
        }
        .security-badge {
            background: #28a745;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-bottom: 10px;
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">
            <div class="security-badge">🔒 ACESSO AUTORIZADO</div>
            <h1>💬 Chat com IA Mamute</h1>
            <p>Converse com a IA mais segura e inteligente!</p>
        </div>
        
        <div style="text-align: center; padding: 50px;">
            <p>🚧 Interface de chat em desenvolvimento...</p>
            <p>✅ Sua autorização foi confirmada</p>
            <p>🔐 Sessão segura estabelecida</p>
            
            <br>
            <a href="/" style="color: #667eea; text-decoration: none;">← Voltar ao início</a>
        </div>
    </div>
</body>
</html>
    """)

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok", "secure": True, "pending_requests": len(security_manager.pending_requests)}

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

if __name__ == "__main__":
    print("""
🔒 ═══════════════════════════════════════════════════════════════════════════
🔒                    IA MAMUTE ULTRA-SEGURA INICIADA                          
🔒 ═══════════════════════════════════════════════════════════════════════════

🔐 SISTEMA DE AUTORIZAÇÃO MANUAL ATIVO

📋 Como funciona:
   1. Usuários solicitam acesso via /request-access
   2. Você recebe notificação no terminal
   3. Acesse http://localhost:8000/admin (admin/mamute2026)
   4. Aprove ou negue cada solicitação manualmente

🌐 URLs:
   • 👤 Acesso público: http://localhost:8000/request-access  
   • 🔒 Painel admin: http://localhost:8000/admin
   • 📱 Rede local: http://192.168.1.70:8000/request-access

⚠️ CONFIGURAÇÕES DE SEGURANÇA:
   • ✅ Autorização manual obrigatória
   • ✅ Bloqueio automático de IPs suspeitos
   • ✅ Logs detalhados de todos os acessos
   • ✅ Sessões com expiração (1 hora)
   • ✅ Rate limiting por IP

🔑 Login Admin: admin / mamute2026 (ALTERE ESTA SENHA!)

🔒 ═══════════════════════════════════════════════════════════════════════════
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",  # Permitir acesso externo
        port=8000,
        reload=False,  # Desabilitar reload em produção
        log_level="info"
    )