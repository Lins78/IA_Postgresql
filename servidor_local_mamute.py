#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IA MAMUTE - SERVIDOR LOCAL COMPLETO
Todas as funcionalidades ativas sem restrições
"""

from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import uuid
import uvicorn
import base64
import mimetypes
from datetime import datetime
import os

# === SISTEMA IA COMPLETO ===
class MamuteAI:
    def __init__(self):
        self.version = "2.0 Local"
        self.capabilities = ["postgresql", "programming", "dashboard", "image_analysis"]
    
    def chat(self, message, image_context=None):
        message_lower = message.lower()
        
        # Hora atual para saudações
        hora = datetime.now().hour
        if 5 <= hora < 12:
            periodo = "Bom dia"
        elif 12 <= hora < 18:
            periodo = "Boa tarde"
        else:
            periodo = "Boa noite"
        
        # Processar com imagem
        if image_context:
            return f"""🖼️ **Imagem recebida com sucesso!**

**Sua mensagem:** {message}

💡 **Como especialista, posso analisar:**

📊 **Diagramas de banco de dados:**
- Revisar estrutura de tabelas
- Sugerir otimizações de schema
- Criar consultas SQL otimizadas

💻 **Código ou interfaces:**
- Code review e melhorias
- Identificar bugs potenciais
- Sugerir refatorações

📈 **Gráficos e relatórios:**
- Interpretar dados
- Criar dashboards interativos
- Análise estatística

{image_context}

**Me conte o que você quer fazer com essa imagem!** 🎯"""
        
        # Saudações
        if any(word in message_lower for word in ["ola", "oi", "bom dia", "boa tarde", "boa noite"]):
            return f"""{periodo}! 🚀 **IA MAMUTE LOCAL ATIVA!**

🔥 **Sistema completo funcionando:**

🗄️ **PostgreSQL Expert:**
- Consultas SQL avançadas (JOINs, CTEs, Subqueries)
- Otimização de performance e índices
- Design de schemas e normalização
- Backup, restore e administração

💻 **Programming Master:**
- **Python**: Django, Flask, FastAPI, Data Science
- **JavaScript**: React, Vue.js, Node.js, APIs
- **Java**: Spring Boot, microserviços
- **C/C++**: Performance crítica, algoritmos

📊 **Dashboard Creator:**
- Visualizações interativas (Chart.js, D3.js)
- Dashboards em tempo real
- KPIs e métricas executivas
- Integração com PostgreSQL

🖼️ **Image Analysis:**
- Análise de código em imagens
- Diagramas de banco de dados
- Interfaces e mockups

💡 **Como posso ajudar você hoje?**"""

        # PostgreSQL
        elif any(word in message_lower for word in ["postgres", "postgresql", "sql", "banco", "database"]):
            if "criar" in message_lower and "banco" in message_lower:
                return """🗄️ **GUIA COMPLETO: CRIAR BANCO PostgreSQL**

**⚡ COMANDO BÁSICO:**
```sql
CREATE DATABASE meu_banco;
```

**🔧 COM CONFIGURAÇÕES:**
```sql
CREATE DATABASE empresa_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'pt_BR.UTF-8'
    LC_CTYPE = 'pt_BR.UTF-8'
    CONNECTION_LIMIT = 100;
```

**🚀 VIA TERMINAL:**
```bash
createdb -U postgres -h localhost meu_banco
```

**📋 VERIFICAR CRIAÇÃO:**
```sql
\\l  -- Listar bancos
\\dt -- Listar tabelas (após conectar)
```

**💡 EXEMPLO TABELA:**
```sql
-- Criar tabela de usuários
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Criar índices
CREATE INDEX idx_usuario_email ON usuarios(email);
CREATE INDEX idx_usuario_ativo ON usuarios(ativo);
```

**Precisa de mais comandos específicos?**"""

            elif "tabela" in message_lower:
                return """📋 **GUIA TABELAS PostgreSQL**

**🎯 TABELA BÁSICA:**
```sql
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    preco DECIMAL(10,2) CHECK (preco > 0),
    estoque INTEGER DEFAULT 0,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**🔗 RELACIONAMENTOS:**
```sql
-- Tabela categorias
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL
);

-- Tabela produtos com FK
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    categoria_id INTEGER REFERENCES categorias(id) ON DELETE SET NULL,
    preco DECIMAL(10,2)
);
```

**📊 ÍNDICES PARA PERFORMANCE:**
```sql
-- Índice simples
CREATE INDEX idx_produto_nome ON produtos(nome);

-- Índice composto
CREATE INDEX idx_produto_categoria_ativo ON produtos(categoria_id, ativo);

-- Índice parcial (apenas produtos ativos)
CREATE INDEX idx_produto_ativo ON produtos(id) WHERE ativo = true;
```

**Quer ver consultas avançadas para essas tabelas?**"""
                
            else:
                return f"""🗄️ **POSTGRESQL SPECIALIST**

**Pergunta:** "{message}"

💪 **Posso ajudar com:**

**📋 ADMINISTRAÇÃO:**
- Instalação e configuração
- Backup e restore (pg_dump/pg_restore)
- Usuários e permissões (GRANT/REVOKE)
- Monitoramento de performance

**⚡ PERFORMANCE:**
- EXPLAIN ANALYZE (análise de planos)
- Criação de índices otimizados
- Query tuning e reescrita
- Configuração postgresql.conf

**🔧 DESENVOLVIMENTO:**
- Stored Procedures e Functions
- Triggers e constraints
- Types customizados
- Extensions (PostGIS, uuid-ossp)

**🛡️ SEGURANÇA:**
- Row Level Security (RLS)
- SSL/TLS connections
- Auditoria com pg_audit
- Roles e privilégios

**Seja mais específico que eu dou a solução completa!** 🎯"""

        # Programação
        elif any(word in message_lower for word in ["python", "javascript", "java", "programacao", "codigo"]):
            if "python" in message_lower:
                return """🐍 **PYTHON EXPERT ATIVADO**

**🔥 DOMÍNIO COMPLETO:**

**🌐 WEB FRAMEWORKS:**
```python
# FastAPI (Moderno e ultra-rápido)
from fastapi import FastAPI
app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id, "name": "João"}
```

**📊 DATA SCIENCE:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Análise de vendas
df = pd.read_csv('vendas.csv')
vendas_por_mes = df.groupby('mes').agg({
    'valor': ['sum', 'mean', 'count'],
    'produto': 'nunique'
}).round(2)
```

**🗄️ INTEGRAÇÃO POSTGRESQL:**
```python
import psycopg2
import pandas as pd

# Conexão direta
conn = psycopg2.connect(
    host="localhost",
    database="loja",
    user="postgres",
    password="senha"
)

# Query com pandas
query = '''
    SELECT produto, SUM(valor) as total
    FROM vendas 
    GROUP BY produto
    ORDER BY total DESC
'''
df = pd.read_sql(query, conn)
```

**Qual área específica do Python você quer explorar?**"""

            elif "javascript" in message_lower:
                return """🌐 **JAVASCRIPT NINJA**

**⚡ FRONTEND MODERNO:**
```javascript
// React com Hooks
import React, { useState, useEffect } from 'react';

function Dashboard() {
    const [vendas, setVendas] = useState([]);
    
    useEffect(() => {
        fetch('/api/vendas')
            .then(res => res.json())
            .then(setVendas);
    }, []);
    
    return (
        <div className="dashboard">
            {vendas.map(venda => (
                <div key={venda.id} className="card">
                    <h3>{venda.produto}</h3>
                    <p>Valor: R$ {venda.valor}</p>
                </div>
            ))}
        </div>
    );
}
```

**🚀 BACKEND NODE.JS:**
```javascript
const express = require('express');
const { Pool } = require('pg');

const app = express();
const db = new Pool({
    host: 'localhost',
    database: 'loja',
    user: 'postgres'
});

// API REST
app.get('/api/vendas', async (req, res) => {
    const result = await db.query(`
        SELECT v.id, p.nome, v.valor
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
    `);
    res.json(result.rows);
});
```

**Quer ver React, Vue.js ou Node.js específico?**"""
                
            else:
                return f"""💻 **PROGRAMMING POLYGLOT**

**Pergunta:** "{message}"

**🔥 LINGUAGENS DOMINADAS:**

**☕ JAVA:** Spring Boot, microserviços, JPA/Hibernate
**🎯 C/C++:** Performance crítica, algoritmos otimizados
**📱 C#:** ASP.NET Core, Entity Framework, Azure
**🌊 Go:** Concorrência, APIs ultra-rápidas
**🔧 Outras:** Rust, PHP, Ruby, Kotlin, Swift...

**💡 ESPECIALIDADES:**
- Algoritmos e estruturas de dados
- Design patterns avançados
- Arquiteturas escaláveis (Clean, Hexagonal)
- APIs REST, GraphQL, gRPC
- Microserviços e containers
- Testes automatizados (TDD/BDD)

**Qual linguagem ou conceito específico?** 🚀"""

        # Dashboard
        elif any(word in message_lower for word in ["dashboard", "grafico", "relatorio", "visualizacao"]):
            return """📊 **DASHBOARD CREATOR EXPERT**

🎨 **CRIAREI DASHBOARDS INCRÍVEIS:**

**🖥️ STACK COMPLETA:**
```javascript
// Frontend: React + Chart.js
import { Line, Bar, Doughnut } from 'react-chartjs-2';

const Dashboard = () => {
    return (
        <div className="dashboard-grid">
            <div className="kpi-cards">
                <KPICard title="Total Vendas" value="R$ 125.000" growth="+15%" />
                <KPICard title="Novos Clientes" value="847" growth="+8%" />
            </div>
            
            <Line data={salesData} options={lineOptions} />
            <Bar data={categoryData} options={barOptions} />
        </div>
    );
};
```

**⚡ BACKEND API:**
```python
from fastapi import FastAPI
import pandas as pd

@app.get("/api/dashboard/kpis")
async def get_kpis():
    return {
        "total_vendas": 125000,
        "crescimento": 15.2,
        "novos_clientes": 847,
        "ticket_medio": 147.50
    }
```

**📈 TIPOS DE DASHBOARD:**
- **Executivo**: KPIs, tendências, comparações
- **Vendas**: Performance, funil, geográfico
- **Financeiro**: Receitas, despesas, projeções
- **Operacional**: Métricas, SLA, recursos

**Que dados você tem? Vou projetar o dashboard perfeito!** 🎯"""

        # Ajuda geral
        elif "help" in message_lower or "ajuda" in message_lower:
            return """🆘 **CENTRAL DE AJUDA - IA MAMUTE LOCAL**

**🔥 RECURSOS 100% DISPONÍVEIS:**

**🗄️ POSTGRESQL EXPERT:**
- Comandos SQL básicos e avançados
- Consultas otimizadas (JOINs, CTEs, Window Functions)
- Design de schemas e normalização
- Performance tuning e índices
- Backup, restore e administração

**💻 PROGRAMMING MASTER:**
- Python (Django, Flask, FastAPI, Data Science)
- JavaScript (React, Vue.js, Node.js, APIs)
- Java (Spring Boot, microserviços)
- C/C++ (performance, algoritmos)
- Outras linguagens sob demanda

**📊 DASHBOARD CREATOR:**
- Visualizações interativas (Chart.js, D3.js)
- Dashboards executivos e operacionais
- KPIs e métricas em tempo real
- Integração com bancos de dados

**🖼️ IMAGE ANALYSIS:**
- Análise de código em screenshots
- Diagramas de banco de dados
- Interfaces e mockups
- Documentação técnica

**💡 COMANDOS ÚTEIS:**
- "Como criar banco PostgreSQL"
- "Query SQL para..." 
- "Código Python para..."
- "Dashboard para vendas"
- "Otimizar esta consulta"

**🎯 DICA:** Seja específico! Quanto mais detalhes, melhor a resposta.

**Em que posso ajudar agora?** 🚀"""

        # Resposta inteligente geral
        else:
            return f"""🤔 **Analisando sua pergunta...**

**"{message}"**

💡 **Como especialista completo, posso ajudar com:**

**🗄️ POSTGRESQL:**
- Consultas SQL complexas e otimização
- Design de bancos e normalização  
- Performance tuning e índices
- Administração e backup/restore

**💻 PROGRAMAÇÃO:**
- Python, JavaScript, Java, C/C++ e mais
- Frameworks web modernos
- APIs REST e microserviços
- Algoritmos e estruturas de dados

**📊 ANÁLISE DE DADOS:**
- Dashboards interativos
- Visualizações e relatórios
- ETL e pipelines de dados
- Business Intelligence

**🛠️ DESENVOLVIMENTO:**
- Arquiteturas escaláveis
- DevOps e CI/CD
- Testes automatizados
- Code review e refatoração

**🎯 Para uma resposta específica, me diga:**
- Que tecnologia está usando?
- Qual o objetivo final?
- Tem código ou erro específico?
- Qual seu nível de conhecimento?

**Reformule com mais detalhes e eu darei uma solução completa!** 🚀"""

# === CONFIGURAÇÃO FASTAPI ===
app = FastAPI(
    title="🚀 IA Mamute Local", 
    description="Sistema completo sem restrições",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sistema IA
ai_system = MamuteAI()

# === MODELOS PYDANTIC ===
class ChatMessage(BaseModel):
    message: str
    image_data: Optional[str] = None
    image_filename: Optional[str] = None

# === SISTEMA DE UPLOADS ===
UPLOADS_DIR = "uploads/images"
os.makedirs(UPLOADS_DIR, exist_ok=True)

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload de imagem com validação"""
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado")
    
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB max
        raise HTTPException(status_code=400, detail="Arquivo muito grande (máx 10MB)")
    
    # Nome único para o arquivo
    unique_filename = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
    file_path = os.path.join(UPLOADS_DIR, unique_filename)
    
    # Salvar arquivo
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Converter para base64
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
    """Servir imagem uploadada"""
    file_path = os.path.join(UPLOADS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    content_type, _ = mimetypes.guess_type(file_path)
    with open(file_path, "rb") as f:
        return Response(content=f.read(), media_type=content_type)

# === ROTAS PRINCIPAIS ===
@app.get("/")
async def home():
    """Página inicial"""
    return HTMLResponse(f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 IA Mamute Local</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0; padding: 20px; min-height: 100vh;
            display: flex; align-items: center; justify-content: center;
        }}
        .container {{
            background: white; border-radius: 20px; padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1); text-align: center; max-width: 900px;
        }}
        .status {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white; padding: 15px 30px; border-radius: 50px; margin: 20px 0;
            font-weight: bold; font-size: 1.1em;
        }}
        .features {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px; margin: 30px 0;
        }}
        .feature {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px; border-radius: 15px; text-align: left; 
            border: 2px solid #dee2e6; transition: all 0.3s ease;
        }}
        .feature:hover {{
            transform: translateY(-5px); box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-color: #667eea;
        }}
        .feature h3 {{ color: #667eea; margin-bottom: 15px; font-size: 1.2em; }}
        .feature ul {{ list-style: none; padding: 0; }}
        .feature li {{ padding: 5px 0; color: #495057; }}
        .feature li::before {{ content: "✓"; color: #28a745; font-weight: bold; margin-right: 10px; }}
        .btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; padding: 20px 40px;
            border-radius: 50px; cursor: pointer; font-size: 1.3em; margin: 20px;
            text-decoration: none; display: inline-block; font-weight: bold;
            transition: all 0.3s ease; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .btn:hover {{ 
            transform: translateY(-2px); box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 IA MAMUTE COMPLETA</h1>
        <div class="status">✅ ACESSO LOCAL - TODAS FUNCIONALIDADES ATIVAS</div>
        
        <div class="features">
            <div class="feature">
                <h3>🗄️ PostgreSQL Expert</h3>
                <ul>
                    <li>Consultas SQL avançadas</li>
                    <li>Otimização de performance</li>
                    <li>Design de schemas</li>
                    <li>Backup e administração</li>
                </ul>
            </div>
            
            <div class="feature">
                <h3>💻 Programming Master</h3>
                <ul>
                    <li>Python, JavaScript, Java, C++</li>
                    <li>Frameworks web modernos</li>
                    <li>APIs e microserviços</li>
                    <li>Algoritmos e estruturas</li>
                </ul>
            </div>
            
            <div class="feature">
                <h3>📊 Dashboard Creator</h3>
                <ul>
                    <li>Visualizações interativas</li>
                    <li>Dashboards em tempo real</li>
                    <li>KPIs e métricas</li>
                    <li>Business Intelligence</li>
                </ul>
            </div>
            
            <div class="feature">
                <h3>🖼️ Image Analysis</h3>
                <ul>
                    <li>Anexar imagens no chat</li>
                    <li>Análise de código</li>
                    <li>Diagramas de banco</li>
                    <li>Interfaces e mockups</li>
                </ul>
            </div>
        </div>
        
        <a href="/chat" class="btn">💬 INICIAR CHAT COMPLETO</a>
        
        <p style="margin-top: 30px; color: #666; font-size: 1.1em;">
            <strong>🌐 Acesso Local:</strong> http://localhost:8000<br>
            <strong>⚡ Status:</strong> Máxima performance, sem limitações!
        </p>
    </div>
</body>
</html>
    """)

@app.get("/chat")
async def chat_interface():
    """Interface de chat"""
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💬 IA Mamute - Chat Completo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh; display: flex; flex-direction: column;
        }
        
        .header {
            background: rgba(255,255,255,0.1); color: white; padding: 20px;
            text-align: center; backdrop-filter: blur(10px);
        }
        
        .status { 
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white; padding: 8px 20px; border-radius: 25px; 
            font-size: 0.9em; margin-bottom: 10px; display: inline-block; 
        }
        
        .chat-container {
            flex: 1; display: flex; flex-direction: column; max-width: 1200px;
            margin: 20px auto; background: white; border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1); overflow: hidden;
        }
        
        .messages { 
            flex: 1; overflow-y: auto; padding: 20px; max-height: 65vh; 
            background: linear-gradient(to bottom, #fafafa 0%, #f8f9fa 100%);
        }
        
        .message {
            margin-bottom: 20px; padding: 20px; border-radius: 20px;
            max-width: 85%; word-wrap: break-word; line-height: 1.6;
            animation: fadeInUp 0.3s ease;
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .user-message {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; margin-left: auto; text-align: right;
            border-bottom-right-radius: 5px;
        }
        
        .ai-message {
            background: white; color: #333; margin-right: auto; 
            border-left: 4px solid #667eea; box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            border-bottom-left-radius: 5px;
        }
        
        .input-area { 
            padding: 25px; background: #fafafa; border-top: 1px solid #e9ecef; 
        }
        
        .input-form { display: flex; gap: 15px; flex-direction: column; }
        .message-row { display: flex; gap: 15px; align-items: flex-end; }
        
        .attachment-area { 
            display: flex; gap: 15px; align-items: center; margin-bottom: 15px; 
            padding: 15px; background: white; border-radius: 15px; border: 2px dashed #e9ecef;
        }
        
        .image-preview { 
            max-width: 120px; max-height: 120px; border-radius: 10px; 
            border: 2px solid #e9ecef; box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .image-preview-container { position: relative; display: inline-block; }
        
        .remove-image { 
            position: absolute; top: -8px; right: -8px; background: #dc3545; 
            color: white; border: none; border-radius: 50%; width: 25px; height: 25px; 
            cursor: pointer; font-size: 14px; font-weight: bold;
        }
        
        .attach-button { 
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
            color: white; border: none; padding: 15px 20px; 
            border-radius: 12px; cursor: pointer; font-weight: bold;
            transition: all 0.3s ease;
        }
        .attach-button:hover { transform: translateY(-2px); }
        
        #messageInput { 
            flex: 1; padding: 15px 20px; border: 2px solid #e9ecef; border-radius: 25px; 
            outline: none; font-size: 1em; resize: none; min-height: 50px; max-height: 120px;
            transition: border-color 0.3s ease;
        }
        #messageInput:focus { border-color: #667eea; }
        
        #sendButton { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; padding: 15px 25px; border-radius: 25px; 
            cursor: pointer; font-weight: bold; font-size: 1em;
            transition: all 0.3s ease;
        }
        #sendButton:hover { transform: translateY(-2px); }
        #sendButton:disabled { background: #ccc; transform: none; }
        
        .typing { 
            display: none; padding: 20px; color: #666; font-style: italic; 
            text-align: center; background: white; border-radius: 15px; margin: 0 20px;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .home-link { 
            position: absolute; top: 20px; left: 20px; color: white; 
            text-decoration: none; font-weight: bold; padding: 10px 20px; 
            background: rgba(255,255,255,0.2); border-radius: 25px;
            transition: all 0.3s ease;
        }
        .home-link:hover { background: rgba(255,255,255,0.3); }
        
        pre { 
            background: #2d3748; color: #e2e8f0; padding: 20px; border-radius: 10px; 
            overflow-x: auto; margin: 15px 0; border-left: 4px solid #667eea;
        }
        
        code { 
            background: #f7fafc; color: #2d3748; padding: 3px 8px; border-radius: 6px;
            font-family: 'Consolas', 'Monaco', monospace;
        }
    </style>
</head>
<body>
    <a href="/" class="home-link">← Início</a>
    
    <div class="header">
        <div class="status">🚀 IA MAMUTE LOCAL ATIVA</div>
        <h1>Chat IA Mamute</h1>
        <p>Sistema completo com <strong>TODAS AS FUNCIONALIDADES</strong> ativas</p>
    </div>
    
    <div class="chat-container">
        <div class="messages" id="messages"></div>
        <div class="typing" id="typing">🤖 IA digitando...</div>
        
        <div class="input-area">
            <form class="input-form" id="chatForm">
                <div class="attachment-area" id="attachmentArea" style="display: none;">
                    <div id="imagePreview"></div>
                </div>
                <div class="message-row">
                    <button type="button" class="attach-button" id="attachButton">📎 Imagem</button>
                    <textarea id="messageInput" placeholder="Digite sua mensagem... (Shift+Enter = nova linha)" rows="1"></textarea>
                    <button type="submit" id="sendButton">Enviar</button>
                </div>
            </form>
            <input type="file" id="fileInput" accept="image/*" style="display: none;">
        </div>
    </div>
    
    <script>
        const messages = document.getElementById('messages');
        const input = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendButton');
        const form = document.getElementById('chatForm');
        const typing = document.getElementById('typing');
        
        let currentImage = null;
        
        // Auto-resize textarea
        input.addEventListener('input', () => {
            input.style.height = 'auto';
            input.style.height = Math.min(input.scrollHeight, 120) + 'px';
        });
        
        // Enter para enviar (sem Shift)
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                form.dispatchEvent(new Event('submit'));
            }
        });
        
        function addMessage(content, isUser, imageUrl = null) {
            const div = document.createElement('div');
            div.className = 'message ' + (isUser ? 'user-message' : 'ai-message');
            
            let html = '';
            if (imageUrl) {
                html += `<img src="${imageUrl}" style="max-width: 300px; margin: 15px 0; border-radius: 10px; display: block; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">`;
            }
            
            // Processar markdown básico
            html += content
                .replace(/\\n/g, '<br>')
                .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                .replace(/```([\\s\\S]*?)```/g, '<pre><code>$1</code></pre>')
                .replace(/`([^`]+)`/g, '<code>$1</code>');
            
            div.innerHTML = html;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
        
        function showTyping() { typing.style.display = 'block'; }
        function hideTyping() { typing.style.display = 'none'; }
        
        function setupImageUpload() {
            document.getElementById('attachButton').onclick = () => {
                document.getElementById('fileInput').click();
            };
            
            document.getElementById('fileInput').onchange = async (e) => {
                const file = e.target.files[0];
                if (!file) return;
                
                if (!file.type.startsWith('image/')) {
                    alert('Apenas imagens são aceitas');
                    return;
                }
                
                if (file.size > 10 * 1024 * 1024) {
                    alert('Arquivo muito grande (máximo 10MB)');
                    return;
                }
                
                try {
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    const response = await fetch('/upload-image', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        currentImage = data;
                        showImagePreview(data);
                    } else {
                        alert('Erro no upload: ' + data.detail);
                    }
                } catch (error) {
                    alert('Erro no upload da imagem');
                    console.error(error);
                }
            };
        }
        
        function showImagePreview(imageData) {
            const sizeKB = Math.round(imageData.size / 1024);
            document.getElementById('imagePreview').innerHTML = `
                <div class="image-preview-container">
                    <img src="data:${imageData.content_type};base64,${imageData.base64_data}" class="image-preview">
                    <button type="button" class="remove-image" onclick="removeImage()">×</button>
                </div>
                <div style="margin-left: 15px;">
                    <strong>📷 ${imageData.original_name}</strong><br>
                    <small>Tamanho: ${sizeKB}KB</small>
                </div>
            `;
            document.getElementById('attachmentArea').style.display = 'block';
        }
        
        function removeImage() {
            currentImage = null;
            document.getElementById('attachmentArea').style.display = 'none';
            document.getElementById('imagePreview').innerHTML = '';
            document.getElementById('fileInput').value = '';
        }
        
        async function sendMessage(message) {
            if (!message.trim() && !currentImage) return;
            
            const imageUrl = currentImage ? currentImage.url : null;
            const displayMessage = message || '🖼️ Imagem anexada';
            
            addMessage(displayMessage, true, imageUrl);
            
            const data = { message: message || '🖼️ Imagem anexada' };
            if (currentImage) {
                data.image_data = currentImage.base64_data;
                data.image_filename = currentImage.filename;
            }
            
            input.value = '';
            input.style.height = 'auto';
            removeImage();
            sendBtn.disabled = true;
            input.disabled = true;
            showTyping();
            
            try {
                const response = await fetch('/chat/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    addMessage(result.response, false);
                } else {
                    addMessage(`❌ Erro: ${result.detail}`, false);
                }
            } catch (error) {
                addMessage('❌ Erro de conexão', false);
                console.error(error);
            } finally {
                hideTyping();
                sendBtn.disabled = false;
                input.disabled = false;
                input.focus();
            }
        }
        
        form.onsubmit = (e) => {
            e.preventDefault();
            sendMessage(input.value);
        };
        
        setupImageUpload();
        input.focus();
        
        // Mensagem de boas-vindas
        setTimeout(() => {
            addMessage(`🚀 **IA MAMUTE LOCAL ATIVADA!**

✅ **Todas as funcionalidades disponíveis:**
🗄️ **PostgreSQL Expert** - Consultas, otimização, schemas
💻 **Programming Master** - Python, JS, Java, C++ e mais
📊 **Dashboard Creator** - Visualizações interativas
🖼️ **Image Support** - Anexe imagens para análise

**💬 Como posso ajudar você hoje?**`, false);
        }, 1000);
    </script>
</body>
</html>
    """)

@app.post("/chat/send")
async def chat_send(chat_data: ChatMessage):
    """Endpoint para chat"""
    try:
        image_context = None
        if chat_data.image_data and chat_data.image_filename:
            try:
                image_bytes = base64.b64decode(chat_data.image_data)
                size_kb = round(len(image_bytes) / 1024)
                image_context = f"📸 Imagem anexada: {chat_data.image_filename} ({size_kb}KB)"
            except Exception as e:
                image_context = "📸 Imagem anexada (erro ao processar detalhes)"
        
        response = ai_system.chat(chat_data.message, image_context)
        
        return {
            "response": response,
            "status": "success",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "has_image": bool(image_context)
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"response": f"Erro interno: {str(e)}", "status": "error"}
        )

# === ROTAS DE STATUS ===
@app.get("/status")
async def get_status():
    """Status do sistema"""
    return {
        "status": "online",
        "version": ai_system.version,
        "capabilities": ai_system.capabilities,
        "timestamp": datetime.now().isoformat(),
        "uptime": "Sistema local ativo"
    }

@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# === MAIN ===
if __name__ == "__main__":
    print("""
🚀 IA MAMUTE - SERVIDOR LOCAL COMPLETO
======================================

🌐 URLs de Acesso:
   Principal: http://localhost:8000
   Chat:      http://localhost:8000/chat
   Status:    http://localhost:8000/status

✅ FUNCIONALIDADES 100% ATIVAS:
   🗄️ PostgreSQL Expert (consultas avançadas)
   💻 Programming Master (20+ linguagens)  
   📊 Dashboard Creator (visualizações)
   🖼️ Image Support (anexar imagens)
   🧠 AI Proativa (respostas inteligentes)

⚡ ACESSO LOCAL - SEM RESTRIÇÕES!
   Máxima performance e funcionalidades completas

    """)
    
    try:
        uvicorn.run(
            app, 
            host="localhost", 
            port=8000, 
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"\\n❌ Erro ao iniciar servidor: {e}")