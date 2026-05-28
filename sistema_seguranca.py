"""
Sistema de Autorização Manual Ultra-Seguro para IA Mamute
Controle total sobre quem acessa sua IA
"""
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
import time
import json
import hashlib
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict

# Sistema de Segurança
security = HTTPBasic()
bearer_security = HTTPBearer()

class SecurityManager:
    def __init__(self):
        self.pending_requests = {}
        self.approved_sessions = {}
        self.blocked_ips = set()
        self.access_logs = []
        self.admin_sessions = set()
        self.failed_attempts = defaultdict(int)
        
    def create_access_request(self, client_ip: str, user_agent: str, path: str) -> str:
        """Criar solicitação de acesso"""
        
        # Verificar se IP está bloqueado
        if self.is_ip_blocked(client_ip):
            raise HTTPException(status_code=403, detail="IP bloqueado")
            
        # Verificar tentativas falhas
        if self.failed_attempts[client_ip] >= 5:
            self.blocked_ips.add(client_ip)
            raise HTTPException(status_code=403, detail="Muitas tentativas. IP bloqueado")
        
        request_id = str(uuid.uuid4())
        self.pending_requests[request_id] = {
            'id': request_id,
            'ip': client_ip,
            'user_agent': user_agent,
            'path': path,
            'timestamp': datetime.now(),
            'status': 'pending',
            'location': self.get_location(client_ip),
            'risk_level': self.assess_risk(client_ip, user_agent)
        }
        
        # Log da tentativa
        self.log_access('access_requested', client_ip, {'request_id': request_id, 'path': path})
        
        print(f"""
🚨 NOVA SOLICITAÇÃO DE ACESSO!
━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 IP: {client_ip}
🌍 Local: {self.get_location(client_ip)}
🖥️ Dispositivo: {user_agent[:50]}...
📄 Página: {path}
⚠️ Risco: {self.assess_risk(client_ip, user_agent)}
🆔 ID: {request_id}
⏰ {datetime.now().strftime('%H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Acesse o painel: http://localhost:8000/admin
🔐 Autorize ou bloqueie este acesso!
        """)
        
        return request_id
        
    def get_location(self, ip: str) -> str:
        """Identificar localização do IP"""
        if ip in ['127.0.0.1', 'localhost']:
            return '🏠 Localhost'
        elif ip.startswith(('192.168.', '10.', '172.')):
            return '🏠 Rede Local'
        else:
            return '🌍 Internet'
            
    def assess_risk(self, ip: str, user_agent: str) -> str:
        """Avaliar risco da solicitação"""
        risk_score = 0
        
        # IP externo
        if not ip.startswith(('192.168.', '10.', '172.', '127.')):
            risk_score += 2
            
        # User agent suspeito
        suspicious_agents = ['bot', 'crawl', 'spider', 'scan', 'automated']
        if any(word in user_agent.lower() for word in suspicious_agents):
            risk_score += 3
            
        # IP com tentativas anteriores
        if ip in self.blocked_ips or self.failed_attempts[ip] > 0:
            risk_score += 2
            
        if risk_score >= 5:
            return '🔴 ALTO'
        elif risk_score >= 2:
            return '🟡 MÉDIO'
        else:
            return '🟢 BAIXO'
            
    def approve_request(self, request_id: str) -> Optional[str]:
        """Aprovar solicitação"""
        if request_id not in self.pending_requests:
            return None
            
        req = self.pending_requests[request_id]
        session_id = str(uuid.uuid4())
        
        # Criar sessão aprovada (válida por 1 hora)
        self.approved_sessions[session_id] = {
            'ip': req['ip'],
            'approved_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=1),
            'request_id': request_id
        }
        
        req['status'] = 'approved'
        req['session_id'] = session_id
        
        self.log_access('access_approved', req['ip'], {'request_id': request_id})
        
        print(f"✅ ACESSO APROVADO: {req['ip']} - Sessão: {session_id}")
        
        return session_id
        
    def deny_request(self, request_id: str) -> bool:
        """Negar solicitação"""
        if request_id not in self.pending_requests:
            return False
            
        req = self.pending_requests[request_id]
        req['status'] = 'denied'
        
        # Bloquear IP
        self.blocked_ips.add(req['ip'])
        
        self.log_access('access_denied', req['ip'], {'request_id': request_id})
        
        print(f"❌ ACESSO NEGADO: {req['ip']} - IP BLOQUEADO")
        
        return True
        
    def is_session_valid(self, session_id: str, client_ip: str) -> bool:
        """Verificar se sessão é válida"""
        if not session_id or session_id not in self.approved_sessions:
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
        
    def is_ip_blocked(self, ip: str) -> bool:
        """Verificar se IP está bloqueado"""
        return ip in self.blocked_ips
        
    def log_access(self, action: str, ip: str, details: dict = None):
        """Log de acesso"""
        self.access_logs.append({
            'timestamp': datetime.now(),
            'ip': ip,
            'action': action,
            'details': details or {}
        })
        
    def authenticate_admin(self, credentials: HTTPBasicCredentials) -> bool:
        """Autenticar administrador"""
        correct_username = "admin"
        correct_password = "mamute2026"  # ALTERE ESTA SENHA!
        
        is_correct_username = credentials.username == correct_username
        is_correct_password = credentials.password == correct_password
        
        if not (is_correct_username and is_correct_password):
            self.failed_attempts[credentials.username] += 1
            return False
            
        return True

# Instância global
security_manager = SecurityManager()

class AccessRequest(BaseModel):
    message: str = "Solicitando acesso à IA Mamute"

class AdminAction(BaseModel):
    action: str  # "approve" ou "deny"
    request_id: str

# Middleware de segurança
async def require_authorization(request: Request):
    """Middleware que exige autorização para acessar a IA"""
    client_ip = request.client.host
    path = str(request.url.path)
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Rotas administrativas não precisam de autorização da IA
    if path.startswith('/admin') or path.startswith('/static') or path == '/favicon.ico':
        return
    
    # Verificar se é uma solicitação de autorização
    if path == '/request-access':
        return
        
    # Verificar sessão válida
    session_id = request.cookies.get('mamute_session')
    if session_id and security_manager.is_session_valid(session_id, client_ip):
        return
    
    # IP bloqueado
    if security_manager.is_ip_blocked(client_ip):
        raise HTTPException(status_code=403, detail="Acesso bloqueado")
    
    # Criar nova solicitação
    request_id = security_manager.create_access_request(client_ip, user_agent, path)
    
    # Redirecionar para página de espera
    raise HTTPException(
        status_code=401,
        detail={
            "message": "Autorização necessária",
            "request_id": request_id,
            "redirect": f"/wait-approval?request_id={request_id}"
        }
    )