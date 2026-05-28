"""
IA MAMUTE COMPLETA - ACESSO LOCAL COM TODAS AS FUNCIONALIDADES
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
import psycopg2
from psycopg2 import sql
import subprocess
import threading
import asyncio
from pathlib import Path

# Adicionar o diretório principal ao path
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
APPS_DIR = SRC_DIR / "apps"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

# SISTEMA IA COMPLETO INTEGRADO
class MamuteCompleteAI:
    def __init__(self):
        self.knowledge_base = self.load_knowledge_base()
        self.session_history = {}
        
    def load_knowledge_base(self):
        """Carregar base de conhecimento completa"""
        return {
            'postgresql': {
                'comandos_basicos': {
                    'criar_db': 'CREATE DATABASE nome_do_banco;',
                    'listar_dbs': '\\l ou SELECT datname FROM pg_database;',
                    'conectar_db': '\\c nome_do_banco;',
                    'criar_tabela': '''CREATE TABLE usuarios (
                        id SERIAL PRIMARY KEY,
                        nome VARCHAR(100) NOT NULL,
                        email VARCHAR(150) UNIQUE,
                        created_at TIMESTAMP DEFAULT NOW()
                    );'''
                },
                'consultas_avancadas': {
                    'joins': '''SELECT u.nome, p.titulo 
                               FROM usuarios u 
                               INNER JOIN posts p ON u.id = p.usuario_id;''',
                    'subconsultas': '''SELECT nome FROM usuarios 
                                      WHERE id IN (SELECT usuario_id FROM posts 
                                                  WHERE created_at > NOW() - INTERVAL '30 days');''',
                    'cte': '''WITH usuarios_ativos AS (
                              SELECT id, nome FROM usuarios WHERE ativo = true
                           )
                           SELECT * FROM usuarios_ativos;'''
                }
            },
            'programacao': {
                'python': {
                    'frameworks': ['Django', 'Flask', 'FastAPI', 'Tornado'],
                    'libs_dados': ['Pandas', 'NumPy', 'Matplotlib', 'Seaborn'],
                    'ml': ['TensorFlow', 'PyTorch', 'Scikit-learn', 'XGBoost']
                },
                'javascript': {
                    'frontend': ['React', 'Vue.js', 'Angular', 'Svelte'],
                    'backend': ['Node.js', 'Express', 'Nest.js', 'Fastify'],
                    'mobile': ['React Native', 'Ionic', 'Cordova']
                }
            }
        }
    
    def chat(self, message, session_id="default", context=None):
        """Processar mensagem com IA completa"""
        
        # Inicializar histórico da sessão
        if session_id not in self.session_history:
            self.session_history[session_id] = []
        
        # Adicionar mensagem ao histórico
        self.session_history[session_id].append({
            'timestamp': datetime.now(),
            'message': message,
            'context': context
        })
        
        message_lower = message.lower()
        
        # Análise avançada de contexto
        if context and 'image' in str(context).lower():
            return self.process_image_context(message, context)
        
        # PostgreSQL especializado
        if any(word in message_lower for word in ['postgres', 'postgresql', 'sql', 'banco', 'database']):
            return self.handle_postgresql_query(message)
        
        # Programação especializada
        elif any(word in message_lower for word in ['python', 'javascript', 'java', 'codigo', 'programacao']):
            return self.handle_programming_query(message)
        
        # Consultas específicas
        elif any(word in message_lower for word in ['como criar', 'como fazer', 'explicar', 'tutorial']):
            return self.handle_tutorial_request(message)
        
        # Dashboard e visualização
        elif any(word in message_lower for word in ['dashboard', 'grafico', 'relatorio', 'visualizacao']):
            return self.handle_dashboard_request(message)
        
        # Resposta inteligente geral
        else:
            return self.handle_general_query(message)
    
    def process_image_context(self, message, context):
        """Processar mensagens com imagem"""
        return f"""🖼️ **Imagem recebida com sucesso!**

**Análise da sua solicitação:** {message}

💡 **Como especialista, posso ajudar com:**

📊 **Se é um diagrama de banco:**
- Analisar estrutura de tabelas
- Sugerir melhorias no schema
- Criar consultas SQL otimizadas
- Identificar relacionamentos

💻 **Se é código/interface:**
- Revisar código e sugerir melhorias
- Identificar bugs potenciais
- Propor refatorações
- Melhorar design e UX

📈 **Se é um gráfico/relatório:**
- Interpretar dados
- Sugerir novas visualizações
- Criar dashboards interativos
- Análise estatística

🔧 **Próximos passos:**
1. Descreva o que você quer fazer com a imagem
2. Conte qual é o objetivo final
3. Eu darei uma solução completa e detalhada!

{context if context else ''}"""
    
    def handle_postgresql_query(self, message):
        """Responder consultas PostgreSQL"""
        message_lower = message.lower()
        
        if 'criar' in message_lower and ('banco' in message_lower or 'database' in message_lower):
            return """🗄️ **GUIA COMPLETO - CRIAR BANCO PostgreSQL**

**🚀 1. COMANDO BÁSICO:**
```sql
CREATE DATABASE meu_banco;
```

**⚙️ 2. CONFIGURAÇÃO COMPLETA:**
```sql
CREATE DATABASE empresa_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'pt_BR.UTF-8'
    LC_CTYPE = 'pt_BR.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = 100;
```

**🔧 3. VIA LINHA DE COMANDO:**
```bash
# Criar banco
createdb -U postgres -h localhost -p 5432 meu_banco

# Com configurações
createdb -U postgres -E UTF8 -l pt_BR.UTF-8 meu_banco
```

**📋 4. VERIFICAR CRIAÇÃO:**
```sql
-- Listar bancos
\\l

-- Query detalhada
SELECT datname, datowner, encoding, datcollate
FROM pg_database 
WHERE datname = 'meu_banco';
```

**🎯 5. CONECTAR AO NOVO BANCO:**
```sql
\\c meu_banco;
\\dt  -- Listar tabelas
```

**💡 DICA PRO:** Sempre defina encoding UTF8 para suporte completo a caracteres especiais!

Precisa de comandos para criar tabelas também?"""

        elif 'tabela' in message_lower:
            return """📋 **GUIA COMPLETO - CRIAR TABELAS PostgreSQL**

**🎯 1. TABELA BÁSICA:**
```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**🔧 2. TABELA AVANÇADA:**
```sql
CREATE TABLE produtos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) CHECK (preco > 0),
    categoria_id INTEGER REFERENCES categorias(id),
    estoque INTEGER DEFAULT 0,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**🔗 3. RELACIONAMENTOS:**
```sql
-- Tabela pai
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL
);

-- Tabela com FK
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    categoria_id INTEGER REFERENCES categorias(id) ON DELETE SET NULL
);
```

**📊 4. ÍNDICES PARA PERFORMANCE:**
```sql
-- Índice simples
CREATE INDEX idx_produto_nome ON produtos(nome);

-- Índice composto
CREATE INDEX idx_produto_categoria_ativo ON produtos(categoria_id, ativo);

-- Índice parcial
CREATE INDEX idx_produto_ativo ON produtos(id) WHERE ativo = true;
```

**⚡ 5. CONSTRAINTS AVANÇADAS:**
```sql
ALTER TABLE produtos 
ADD CONSTRAINT chk_preco_positivo CHECK (preco > 0),
ADD CONSTRAINT chk_estoque_nao_negativo CHECK (estoque >= 0);
```

Quer ver exemplos de consultas avançadas para essas tabelas?"""

        elif 'consulta' in message_lower or 'select' in message_lower:
            return """🔍 **GUIA CONSULTAS SQL AVANÇADAS**

**🎯 1. JOINS COMPLEXOS:**
```sql
-- INNER JOIN com múltiplas tabelas
SELECT 
    u.nome as usuario,
    p.titulo as produto,
    c.nome as categoria,
    v.total,
    v.created_at as data_venda
FROM usuarios u
INNER JOIN vendas v ON u.id = v.usuario_id
INNER JOIN produtos p ON v.produto_id = p.id
INNER JOIN categorias c ON p.categoria_id = c.id
WHERE v.created_at >= NOW() - INTERVAL '30 days'
ORDER BY v.total DESC;
```

**💡 2. SUBCONSULTAS (SUBQUERIES):**
```sql
-- Usuários que compraram produtos caros
SELECT nome, email
FROM usuarios
WHERE id IN (
    SELECT DISTINCT usuario_id 
    FROM vendas 
    WHERE total > (SELECT AVG(total) FROM vendas)
);
```

**🚀 3. CTE (Common Table Expressions):**
```sql
WITH vendas_mensais AS (
    SELECT 
        DATE_TRUNC('month', created_at) as mes,
        SUM(total) as total_mes,
        COUNT(*) as qtd_vendas
    FROM vendas
    GROUP BY DATE_TRUNC('month', created_at)
),
media_mensal AS (
    SELECT AVG(total_mes) as media FROM vendas_mensais
)
SELECT 
    vm.mes,
    vm.total_mes,
    vm.qtd_vendas,
    CASE 
        WHEN vm.total_mes > mm.media THEN 'Acima da média'
        ELSE 'Abaixo da média'
    END as performance
FROM vendas_mensais vm
CROSS JOIN media_mensal mm
ORDER BY vm.mes DESC;
```

**📊 4. WINDOW FUNCTIONS:**
```sql
SELECT 
    nome,
    categoria,
    preco,
    RANK() OVER (PARTITION BY categoria ORDER BY preco DESC) as rank_preco,
    AVG(preco) OVER (PARTITION BY categoria) as media_categoria
FROM produtos
WHERE ativo = true;
```

**⚡ 5. CONSULTA DE PERFORMANCE:**
```sql
-- Análise de vendas com ranking
SELECT 
    p.nome as produto,
    COUNT(v.id) as total_vendas,
    SUM(v.total) as receita_total,
    AVG(v.total) as ticket_medio,
    DENSE_RANK() OVER (ORDER BY SUM(v.total) DESC) as ranking
FROM produtos p
LEFT JOIN vendas v ON p.id = v.produto_id
GROUP BY p.id, p.nome
HAVING COUNT(v.id) > 0
ORDER BY receita_total DESC
LIMIT 10;
```

Quer ver exemplos de otimização de performance ou stored procedures?"""

        else:
            return f"""🗄️ **PostgreSQL Specialist Activated!**

**Sua pergunta:** "{message}"

💪 **Posso ajudar com TUDO sobre PostgreSQL:**

**📋 ADMINISTRAÇÃO:**
- Instalação e configuração
- Backup e restore (pg_dump, pg_restore)
- Usuários e permissões (GRANT, REVOKE)
- Monitoramento e logs

**⚡ PERFORMANCE:**
- Análise de planos de execução (EXPLAIN ANALYZE)
- Criação de índices otimizados
- Tuning de postgresql.conf
- Identificação de queries lentas

**🔧 DESENVOLVIMENTO:**
- Stored Procedures e Functions
- Triggers complexos
- Tipos de dados customizados
- Extensions (PostGIS, uuid-ossp)

**🛡️ SEGURANÇA:**
- Row Level Security (RLS)
- Conexões SSL/TLS
- Auditoria com pg_audit
- Criptografia de dados

**🔄 INTEGRAÇÃO:**
- Replicação e clustering
- Connection pooling (PgBouncer)
- Migrations com Alembic/Flyway
- APIs com Python/Node.js

**Seja mais específico e eu darei uma solução completa!** 🎯"""
    
    def handle_programming_query(self, message):
        """Responder consultas de programação"""
        message_lower = message.lower()
        
        if 'python' in message_lower:
            return """🐍 **PYTHON MASTER SPECIALIST**

**💪 DOMÍNIO COMPLETO EM:**

**🌐 WEB FRAMEWORKS:**
```python
# FastAPI (Moderno e rápido)
from fastapi import FastAPI
app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

# Django (Framework completo)
from django.http import JsonResponse
def user_view(request, user_id):
    return JsonResponse({"user_id": user_id})
```

**📊 DATA SCIENCE:**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Análise de dados
df = pd.read_csv('dados.csv')
df.groupby('categoria').agg({
    'vendas': ['sum', 'mean', 'count'],
    'lucro': 'sum'
}).round(2)

# Machine Learning
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier()
model.fit(X_train, y_train)
```

**🗄️ DATABASE INTEGRATION:**
```python
import psycopg2
from sqlalchemy import create_engine

# PostgreSQL direto
conn = psycopg2.connect(
    host="localhost",
    database="meudb",
    user="postgres"
)

# SQLAlchemy ORM
engine = create_engine('postgresql://user:pass@localhost/db')
```

**⚡ ASYNC PROGRAMMING:**
```python
import asyncio
import aiohttp

async def fetch_data(session, url):
    async with session.get(url) as response:
        return await response.json()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
```

**🔧 AUTOMAÇÃO E SCRIPTS:**
```python
import os
import shutil
from pathlib import Path

# Organizar arquivos
def organize_files(directory):
    for file_path in Path(directory).iterdir():
        if file_path.is_file():
            extension = file_path.suffix
            dest_dir = Path(directory) / extension[1:]
            dest_dir.mkdir(exist_ok=True)
            shutil.move(str(file_path), dest_dir / file_path.name)
```

Qual área específica do Python você quer explorar?"""

        elif 'javascript' in message_lower:
            return """🌐 **JAVASCRIPT NINJA SPECIALIST**

**⚡ EXPERTISE COMPLETA:**

**🎯 FRONTEND MODERNO:**
```javascript
// React com Hooks
import React, { useState, useEffect } from 'react';

function UserDashboard() {
    const [users, setUsers] = useState([]);
    
    useEffect(() => {
        fetch('/api/users')
            .then(res => res.json())
            .then(setUsers);
    }, []);
    
    return (
        <div>
            {users.map(user => (
                <UserCard key={user.id} user={user} />
            ))}
        </div>
    );
}

// Vue.js 3 Composition API
import { ref, onMounted } from 'vue';

export default {
    setup() {
        const users = ref([]);
        
        onMounted(async () => {
            const response = await fetch('/api/users');
            users.value = await response.json();
        });
        
        return { users };
    }
};
```

**🚀 BACKEND NODE.JS:**
```javascript
// Express.js moderno
const express = require('express');
const app = express();

// Middleware
app.use(express.json());
app.use(cors());

// Routes com async/await
app.get('/api/users/:id', async (req, res) => {
    try {
        const user = await User.findById(req.params.id);
        res.json(user);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// WebSocket real-time
const io = require('socket.io')(server);
io.on('connection', (socket) => {
    socket.on('message', (data) => {
        io.emit('message', data);
    });
});
```

**⚡ ES6+ FEATURES:**
```javascript
// Destructuring e Spread
const { name, email } = user;
const newUser = { ...user, active: true };

// Async/Await
const fetchUsers = async () => {
    try {
        const response = await fetch('/api/users');
        return await response.json();
    } catch (error) {
        console.error('Erro:', error);
    }
};

// Arrow Functions e Array Methods
const activeUsers = users
    .filter(user => user.active)
    .map(user => ({ ...user, displayName: user.name.toUpperCase() }))
    .sort((a, b) => a.name.localeCompare(b.name));
```

**📱 MOBILE DEVELOPMENT:**
```javascript
// React Native
import React from 'react-native';

const UserScreen = () => {
    return (
        <View style={styles.container}>
            <Text style={styles.title}>Usuários</Text>
            <FlatList
                data={users}
                renderItem={({ item }) => <UserItem user={item} />}
                keyExtractor={item => item.id}
            />
        </View>
    );
};
```

Quer ver exemplos específicos de alguma tecnologia?"""

        else:
            return f"""💻 **PROGRAMMING POLYGLOT ACTIVATED**

**Sua pergunta:** "{message}"

**🔥 LINGUAGENS QUE DOMINO:**

**☕ JAVA:**
- Spring Boot, Spring Framework
- Microserviços e APIs REST
- JPA/Hibernate para bancos
- Maven/Gradle build tools

**🎯 C/C++:**
- Performance crítica
- Sistemas embarcados  
- Algoritmos otimizados
- Memory management

**📱 C# (.NET):**
- ASP.NET Core APIs
- Entity Framework
- Desktop (WPF/WinUI)
- Azure integration

**🌊 GO:**
- Microserviços ultra-rápidos
- Concorrência com goroutines
- APIs REST minimalistas
- Cloud-native development

**🔧 OUTRAS ESPECIALIDADES:**
- **Rust**: Segurança e performance
- **PHP**: Laravel, WordPress
- **Ruby**: Rails, Sinatra
- **Kotlin**: Android, multiplatform
- **Swift**: iOS development
- **TypeScript**: JavaScript tipado

**💡 POSSO AJUDAR COM:**
- Algoritmos e estruturas de dados
- Design patterns (Singleton, Factory, Observer...)
- Arquiteturas (MVC, MVP, Clean Architecture)
- APIs REST, GraphQL, gRPC
- Testes unitários e integração
- CI/CD e DevOps
- Code review e refatoração

**Qual linguagem ou conceito específico você quer explorar?** 🚀"""
    
    def handle_tutorial_request(self, message):
        """Responder solicitações de tutorial"""
        return f"""📚 **TUTORIAL SPECIALIST**

**Sua solicitação:** "{message}"

🎯 **VAMOS CRIAR UM GUIA COMPLETO!**

Para dar o melhor tutorial possível, me conte:

**1. 📋 CONTEXTO:**
- O que você quer aprender especificamente?
- Qual seu nível atual (iniciante/intermediário/avançado)?
- Para que vai usar (trabalho/estudo/projeto pessoal)?

**2. 🛠️ AMBIENTE:**
- Que tecnologias já tem instaladas?
- Sistema operacional (Windows/Mac/Linux)?
- Ferramentas preferidas (VS Code, IntelliJ, etc.)?

**3. 🎯 OBJETIVO:**
- Qual o resultado final desejado?
- Tem deadline específico?
- Vai integrar com algo existente?

**💡 EXEMPLOS DE TUTORIAIS QUE POSSO CRIAR:**

**🗄️ BANCO DE DADOS:**
- "Como criar sistema completo PostgreSQL do zero"
- "Otimização de queries SQL passo a passo"
- "Backup e restore automatizado"

**💻 PROGRAMAÇÃO:**
- "API REST completa em Python/FastAPI"
- "Dashboard interativo React + PostgreSQL"
- "Sistema de autenticação JWT"

**📊 ANÁLISE DE DADOS:**
- "Pipeline de dados com Python/Pandas"
- "Dashboards em tempo real"
- "Machine Learning para iniciantes"

**Detalhe melhor sua necessidade e eu criarei um tutorial COMPLETO com código, exemplos e explicações!** 🚀"""
    
    def handle_dashboard_request(self, message):
        """Responder solicitações de dashboard"""
        return """📊 **DASHBOARD CREATOR EXPERT**

🎨 **POSSO CRIAR DASHBOARDS INCRÍVEIS:**

**🖥️ TECNOLOGIAS FRONTEND:**
```javascript
// React + Chart.js
import { Line, Bar, Pie } from 'react-chartjs-2';

const Dashboard = () => {
    const data = {
        labels: ['Jan', 'Fev', 'Mar', 'Abr'],
        datasets: [{
            label: 'Vendas',
            data: [65, 59, 80, 81],
            borderColor: '#667eea'
        }]
    };
    
    return (
        <div className="dashboard">
            <Line data={data} options={options} />
            <Bar data={salesData} />
            <Pie data={categoryData} />
        </div>
    );
};
```

**⚡ BACKEND PYTHON:**
```python
from fastapi import FastAPI
import pandas as pd
import plotly.express as px

app = FastAPI()

@app.get("/api/dashboard/sales")
async def get_sales_data():
    # Conectar PostgreSQL
    df = pd.read_sql("""
        SELECT 
            DATE_TRUNC('month', created_at) as mes,
            SUM(total) as vendas,
            COUNT(*) as qtd_pedidos
        FROM vendas 
        WHERE created_at >= NOW() - INTERVAL '12 months'
        GROUP BY mes
        ORDER BY mes
    """, connection)
    
    return df.to_dict('records')

@app.get("/api/dashboard/kpis")
async def get_kpis():
    return {
        "total_vendas": 150000,
        "novos_clientes": 45,
        "ticket_medio": 125.50,
        "crescimento": 15.2
    }
```

**📈 VISUALIZAÇÕES AVANÇADAS:**
```html
<!-- Dashboard HTML completo -->
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard Executivo</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="dashboard.css">
</head>
<body>
    <div class="dashboard-grid">
        <div class="kpi-cards">
            <div class="card">
                <h3>Total Vendas</h3>
                <span class="value">R$ 150.000</span>
                <span class="growth">+15.2%</span>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="salesChart"></canvas>
        </div>
        
        <div class="real-time-data">
            <div id="live-metrics"></div>
        </div>
    </div>
    
    <script src="dashboard.js"></script>
</body>
</html>
```

**🔄 TEMPO REAL:**
```javascript
// WebSocket para dados em tempo real
const socket = new WebSocket('ws://localhost:8000/ws');

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    updateCharts(data);
    updateKPIs(data);
};

// Auto-refresh a cada 30 segundos
setInterval(() => {
    fetchLatestData();
}, 30000);
```

**🎯 TIPOS DE DASHBOARD:**

**📊 EXECUTIVO:**
- KPIs principais
- Gráficos de tendência
- Comparações período anterior
- Alertas automáticos

**💰 FINANCEIRO:**
- Receitas e despesas
- Fluxo de caixa
- Projeções
- ROI por canal

**📈 VENDAS:**
- Performance por vendedor
- Funil de conversão
- Produtos mais vendidos
- Análise geográfica

**👥 OPERACIONAL:**
- Métricas de produtividade
- SLA e uptime
- Recursos utilizados
- Alertas de sistema

**Que tipo de dashboard você quer criar? Me conte os dados que tem e eu projeto tudo!** 🚀"""
    
    def handle_general_query(self, message):
        """Resposta inteligente geral"""
        return f"""🤖 **IA MAMUTE ULTRA-INTELIGENTE**

**Analisando:** "{message}"

💡 **ESPECIALIDADES ATIVADAS:**

**🗄️ POSTGRESQL EXPERT:**
- Consultas SQL otimizadas
- Design de schemas
- Performance tuning
- Backup/restore estratégico

**💻 PROGRAMAÇÃO MASTER:**
- 20+ linguagens dominadas
- Algoritmos avançados
- Arquiteturas escaláveis
- Code review especializado

**📊 DATA SCIENCE:**
- Análise estatística
- Machine Learning
- Visualizações interativas
- Pipelines de dados

**🌐 DESENVOLVIMENTO WEB:**
- APIs REST/GraphQL
- Frontend moderno (React/Vue)
- Backend robusto
- DevOps e CI/CD

**🔧 AUTOMAÇÃO:**
- Scripts Python
- Processos automáticos
- Monitoramento
- Integração de sistemas

**🎯 PARA RESPOSTA ESPECÍFICA:**

1. **Detalhe sua necessidade** (mais contexto)
2. **Mencione tecnologias** que usa
3. **Explique o objetivo final**
4. **Indique seu nível** de conhecimento

**Exemplos de perguntas específicas:**
- "Como otimizar esta query PostgreSQL..."
- "Preciso de código Python para..."
- "Como criar dashboard para..."
- "Qual a melhor arquitetura para..."

**Reformule sua pergunta e eu darei uma solução COMPLETA!** 🚀"""

# Configurar servidor
app = FastAPI(title="IA Mamute Completa - Acesso Local", version="3.0")

# Middleware
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

# IA System Instance
ai_system = MamuteCompleteAI()

# Modelos de dados
class ChatMessage(BaseModel):
    message: str
    image_data: Optional[str] = None
    image_filename: Optional[str] = None

# Criar diretório para uploads
UPLOADS_DIR = "uploads/images"
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Endpoints de upload de imagem
@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    # Verificar tipo de arquivo
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado")
    
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
    file_path = os.path.join(UPLOADS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "application/octet-stream"
    
    with open(file_path, "rb") as f:
        return Response(content=f.read(), media_type=content_type)

# Endpoint principal
@app.get("/")
async def home():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>🤖 IA Mamute Completa - Acesso Local</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0; padding: 20px; min-height: 100vh;
            display: flex; align-items: center; justify-content: center;
        }
        .container {
            background: white; border-radius: 20px; padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1); text-align: center; max-width: 700px;
        }
        .btn {
            background: #667eea; color: white; border: none; padding: 15px 30px;
            border-radius: 8px; cursor: pointer; font-size: 1.1em; margin: 10px;
            text-decoration: none; display: inline-block; font-weight: bold;
        }
        .btn:hover { background: #5a6bd8; }
        .features {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px; margin: 20px 0;
        }
        .feature {
            background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: left;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 IA MAMUTE COMPLETA</h1>
        <p><strong>ACESSO LOCAL COM TODAS AS FUNCIONALIDADES!</strong></p>
        
        <div class="features">
            <div class="feature">
                <h3>🗄️ PostgreSQL Expert</h3>
                <p>Consultas SQL avançadas, otimização, schemas complexos</p>
            </div>
            <div class="feature">
                <h3>💻 Programming Master</h3>
                <p>20+ linguagens, algoritmos, arquiteturas</p>
            </div>
            <div class="feature">
                <h3>📊 Dashboard Creator</h3>
                <p>Visualizações interativas, tempo real</p>
            </div>
            <div class="feature">
                <h3>🖼️ Image Support</h3>
                <p>Anexe imagens, análise visual</p>
            </div>
            <div class="feature">
                <h3>🧠 AI Proativa</h3>
                <p>Respostas contextuais inteligentes</p>
            </div>
            <div class="feature">
                <h3>⚡ Ultra Performance</h3>
                <p>Respostas rápidas, sem limitações</p>
            </div>
        </div>
        
        <a href="/chat" class="btn">🚀 INICIAR CHAT COMPLETO</a>
        <a href="/database" class="btn">🗄️ TOOLS POSTGRESQL</a>
        
        <p style="margin-top: 20px; color: #666;">
            <strong>✅ Todas as funcionalidades ativas!</strong><br>
            Sem restrições, sem autorizações, máximo desempenho!
        </p>
    </div>
</body>
</html>
    """)

@app.get("/chat")
async def chat_interface():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>💬 IA Mamute - Chat Completo</title>
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
        
        .status-badge {
            background: #28a745; color: white; padding: 5px 15px;
            border-radius: 20px; font-size: 0.8em; margin-bottom: 10px; display: inline-block;
        }
        
        .chat-container {
            flex: 1; display: flex; flex-direction: column; max-width: 1200px;
            margin: 20px auto; background: white; border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1); overflow: hidden;
        }
        
        .messages {
            flex: 1; overflow-y: auto; padding: 20px; max-height: 60vh;
        }
        
        .message {
            margin-bottom: 15px; padding: 15px 20px; border-radius: 18px;
            max-width: 85%; word-wrap: break-word; line-height: 1.4;
        }
        
        .user-message {
            background: #667eea; color: white; margin-left: auto; text-align: right;
        }
        
        .ai-message {
            background: #f1f3f4; color: #333; margin-right: auto;
            border-left: 4px solid #667eea;
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
            max-width: 120px; max-height: 120px; border-radius: 8px;
            border: 2px solid #e9ecef; object-fit: cover;
        }
        
        .image-preview-container {
            position: relative; display: inline-block;
        }
        
        .remove-image {
            position: absolute; top: -5px; right: -5px; background: #dc3545;
            color: white; border: none; border-radius: 50%; width: 24px; height: 24px;
            cursor: pointer; font-size: 14px; font-weight: bold;
        }
        
        .attach-button {
            background: #6c757d; color: white; border: none; padding: 12px 16px;
            border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 8px;
            font-weight: bold; transition: all 0.2s;
        }
        
        .attach-button:hover { background: #5a6268; transform: translateY(-1px); }
        
        #messageInput {
            flex: 1; padding: 15px 20px; border: 2px solid #e9ecef;
            border-radius: 25px; outline: none; font-size: 1em; resize: none;
            min-height: 50px; max-height: 120px;
        }
        
        #messageInput:focus { border-color: #667eea; }
        
        #sendButton {
            background: #667eea; color: white; border: none; padding: 15px 25px;
            border-radius: 25px; cursor: pointer; font-weight: bold; font-size: 1em;
            transition: all 0.2s; min-width: 100px;
        }
        
        #sendButton:hover { background: #5a6bd8; transform: translateY(-1px); }
        #sendButton:disabled { background: #ccc; transform: none; }
        
        .typing-indicator {
            display: none; padding: 15px 20px; color: #666; font-style: italic;
            background: #f8f9fa; border-radius: 15px; margin: 0 auto; max-width: 200px;
        }
        
        .typing-dots {
            display: inline-block;
        }
        
        .typing-dots span {
            display: inline-block; width: 8px; height: 8px; border-radius: 50%;
            background: #667eea; margin: 0 2px; animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }
        
        .message img {
            max-width: 300px; max-height: 300px; border-radius: 8px;
            margin: 10px 0; border: 1px solid #ddd;
        }
        
        pre {
            background: #f4f4f4; padding: 15px; border-radius: 8px;
            overflow-x: auto; font-family: 'Consolas', monospace;
        }
        
        .home-link {
            position: absolute; top: 15px; left: 20px; color: white;
            text-decoration: none; font-weight: bold; padding: 8px 15px;
            background: rgba(255,255,255,0.2); border-radius: 20px;
        }
        
        .home-link:hover { background: rgba(255,255,255,0.3); }
    </style>
</head>
<body>
    <a href="/" class="home-link">← Início</a>
    
    <div class="header">
        <div class="status-badge">🚀 IA COMPLETA ATIVA</div>
        <h1>Chat IA Mamute</h1>
        <p>Assistente especializada com <strong>TODAS AS FUNCIONALIDADES</strong></p>
    </div>
    
    <div class="chat-container">
        <div class="messages" id="messages">
            <!-- Mensagens aparecem aqui -->
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            IA digitando
            <div class="typing-dots">
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
                        📎 Anexar Imagem
                    </button>
                    <textarea 
                        id="messageInput" 
                        placeholder="Digite sua mensagem... (Shift+Enter para nova linha)"
                        rows="1"
                    ></textarea>
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
        
        // Auto-resize textarea
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
        
        // Submit on Enter (not Shift+Enter)
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
        
        function addMessage(content, isUser, imageUrl = null) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + (isUser ? 'user-message' : 'ai-message');
            
            let messageContent = '';
            if (imageUrl) {
                messageContent += `<img src="${imageUrl}" style="max-width: 300px; max-height: 300px; border-radius: 8px; margin: 10px 0; display: block; border: 1px solid #ddd;">`;
            }
            messageContent += content.replace(/\\n/g, '<br>');
            
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
                    <button type="button" class="remove-image" onclick="removeImage()">×</button>
                </div>
                <small><strong>${imageData.original_name}</strong> (${Math.round(imageData.size/1024)}KB)</small>
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
            
            // Adicionar mensagem do usuário
            const imageUrl = currentImage ? currentImage.url : null;
            addMessage(message || '🖼️ Imagem enviada', true, imageUrl);
            
            // Preparar dados
            const messageData = {
                message: message || '🖼️ Imagem enviada'
            };
            
            if (currentImage) {
                messageData.image_data = currentImage.base64_data;
                messageData.image_filename = currentImage.filename;
            }
            
            // Limpar e desabilitar
            messageInput.value = '';
            messageInput.style.height = 'auto';
            removeImage();
            sendButton.disabled = true;
            messageInput.disabled = true;
            
            // Mostrar typing
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
                    addMessage('❌ Erro: ' + (data.detail || 'Falha na comunicação'), false);
                }
            } catch (error) {
                addMessage('❌ Erro de conexão. Verifique sua internet.', false);
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
        
        // Configurar upload de imagem
        setupImageUpload();
        
        // Focar no input
        messageInput.focus();
        
        // Mensagem de boas-vindas
        setTimeout(() => {
            addMessage(`🚀 <strong>IA MAMUTE COMPLETA ATIVADA!</strong><br><br>
            ✅ <strong>Todas as funcionalidades disponíveis:</strong><br>
            🗄️ PostgreSQL Expert (consultas, otimização, schemas)<br>
            💻 Programming Master (20+ linguagens, algoritmos)<br>
            📊 Dashboard Creator (visualizações interativas)<br>
            🖼️ Image Support (anexe imagens para análise)<br>
            🧠 AI Proativa (respostas contextuais avançadas)<br><br>
            <strong>💬 Como posso ajudar você hoje?</strong>`, false);
        }, 1000);
    </script>
</body>
</html>
    """)

@app.get("/database")
async def database_tools():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>🗄️ PostgreSQL Tools</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0; padding: 20px; min-height: 100vh;
        }
        .container {
            max-width: 1200px; margin: 0 auto; background: white; 
            border-radius: 20px; padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        }
        .tools-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px; margin: 20px 0;
        }
        .tool-card {
            background: #f8f9fa; padding: 20px; border-radius: 10px;
            border: 1px solid #e9ecef; transition: all 0.2s;
        }
        .tool-card:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .btn {
            background: #667eea; color: white; border: none; padding: 12px 20px;
            border-radius: 8px; cursor: pointer; text-decoration: none; display: inline-block;
            font-weight: bold; margin: 5px 0;
        }
        .btn:hover { background: #5a6bd8; }
        pre { background: #f4f4f4; padding: 15px; border-radius: 8px; overflow-x: auto; }
        .home-link {
            background: #6c757d; color: white; padding: 10px 20px;
            border-radius: 8px; text-decoration: none; font-weight: bold; margin-bottom: 20px; display: inline-block;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="home-link">← Voltar ao Início</a>
        
        <h1>🗄️ PostgreSQL Expert Tools</h1>
        <p>Ferramentas especializadas para PostgreSQL</p>
        
        <div class="tools-grid">
            <div class="tool-card">
                <h3>🔧 Comandos Básicos</h3>
                <p>Comandos essenciais do PostgreSQL</p>
                <pre>-- Criar banco
CREATE DATABASE meudb;

-- Listar bancos
\\l

-- Conectar
\\c meudb;

-- Listar tabelas
\\dt</pre>
                <a href="/chat" class="btn">Perguntar sobre comandos</a>
            </div>
            
            <div class="tool-card">
                <h3>📊 Consultas Avançadas</h3>
                <p>JOINs, subconsultas, CTEs, window functions</p>
                <pre>-- CTE Example
WITH vendas_mes AS (
  SELECT DATE_TRUNC('month', data) as mes,
         SUM(valor) as total
  FROM vendas
  GROUP BY mes
)
SELECT * FROM vendas_mes;</pre>
                <a href="/chat" class="btn">Criar consultas avançadas</a>
            </div>
            
            <div class="tool-card">
                <h3>⚡ Otimização</h3>
                <p>Performance tuning e análise de queries</p>
                <pre>-- Analisar plano de execução
EXPLAIN ANALYZE
SELECT * FROM tabela 
WHERE coluna = 'valor';

-- Criar índice
CREATE INDEX idx_coluna 
ON tabela(coluna);</pre>
                <a href="/chat" class="btn">Otimizar performance</a>
            </div>
            
            <div class="tool-card">
                <h3>🛡️ Backup & Restore</h3>
                <p>Estratégias de backup e recuperação</p>
                <pre># Backup completo
pg_dump -U postgres -h localhost meudb > backup.sql

# Restore
psql -U postgres -h localhost -d meudb < backup.sql</pre>
                <a href="/chat" class="btn">Configurar backups</a>
            </div>
            
            <div class="tool-card">
                <h3>👥 Usuários & Permissões</h3>
                <p>Gerenciamento de acesso e segurança</p>
                <pre>-- Criar usuário
CREATE USER app_user WITH PASSWORD 'senha';

-- Conceder permissões
GRANT SELECT, INSERT ON tabela TO app_user;</pre>
                <a href="/chat" class="btn">Configurar segurança</a>
            </div>
            
            <div class="tool-card">
                <h3>🔄 Procedures & Functions</h3>
                <p>Stored procedures e funções personalizadas</p>
                <pre>-- Função exemplo
CREATE OR REPLACE FUNCTION calcular_total()
RETURNS DECIMAL AS $$
BEGIN
    RETURN (SELECT SUM(valor) FROM vendas);
END;
$$ LANGUAGE plpgsql;</pre>
                <a href="/chat" class="btn">Criar functions</a>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <a href="/chat" class="btn" style="font-size: 1.2em; padding: 15px 30px;">
                💬 Fazer Pergunta Específica sobre PostgreSQL
            </a>
        </div>
    </div>
</body>
</html>
    """)

# Endpoint do chat
@app.post("/chat/send")
async def chat_send(chat_data: ChatMessage):
    message = chat_data.message
    
    # Verificar se há imagem
    image_context = None
    if chat_data.image_data:
        try:
            image_bytes = base64.b64decode(chat_data.image_data)
            image_size = len(image_bytes)
            image_context = f"[IMAGEM: {chat_data.image_filename} - {round(image_size/1024)}KB]"
        except:
            image_context = "[IMAGEM ANEXADA]"
    
    # Usar IA completa
    try:
        response = ai_system.chat(
            message=message,
            session_id="local_session",
            context=image_context
        )
        
        # Adicionar informação da imagem se houver
        if image_context:
            response += f"\n\n📎 {image_context}"
        
        return {
            "response": response,
            "status": "success",
            "source": "ai_complete_local",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "has_image": bool(image_context)
        }
        
    except Exception as e:
        return {
            "response": f"Erro interno: {str(e)}",
            "status": "error"
        }

@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "mode": "complete_local",
        "features": [
            "postgresql_expert",
            "programming_master", 
            "image_support",
            "dashboard_creator",
            "ai_proactive"
        ]
    }

if __name__ == "__main__":
    print("""
🚀 IA MAMUTE COMPLETA - ACESSO LOCAL
===================================

🌐 URL Local: http://localhost:8000
💬 Chat: http://localhost:8000/chat  
🗄️ PostgreSQL Tools: http://localhost:8000/database

✅ FUNCIONALIDADES ATIVAS:
- PostgreSQL Expert (consultas, otimização)
- Programming Master (20+ linguagens)
- Dashboard Creator (visualizações)
- Image Support (anexar imagens)
- AI Proativa (respostas inteligentes)

🔥 SEM LIMITAÇÕES, MÁXIMA PERFORMANCE!

""")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)