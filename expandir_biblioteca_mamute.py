"""
Expansão da Biblioteca de Conhecimento do Mamute
- Saudações diárias contextuais
- Previsão do tempo para cidades brasileiras  
- Documentação oficial PostgreSQL
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Adicionar src ao path
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
APPS_DIR = SRC_DIR / "apps"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

from src.database.connection import DatabaseManager
from src.utils.config import Config

def get_saudacoes_diarias():
    """Gera saudações contextuais baseadas no horário e data"""
    agora = datetime.now()
    hora = agora.hour
    dia_semana = agora.strftime("%A")
    data_atual = agora.strftime("%d/%m/%Y")
    
    # Mapeamento de dias da semana
    dias = {
        'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 
        'Wednesday': 'Quarta-feira', 'Thursday': 'Quinta-feira',
        'Friday': 'Sexta-feira', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
    }
    
    dia_pt = dias.get(dia_semana, dia_semana)
    
    # Saudações por horário
    if 5 <= hora < 12:
        periodo = "manhã"
        saudacao = "Bom dia"
        emoji = "🌅"
    elif 12 <= hora < 18:
        periodo = "tarde" 
        saudacao = "Boa tarde"
        emoji = "☀️"
    else:
        periodo = "noite"
        saudacao = "Boa noite"
        emoji = "🌙"
    
    saudacoes_content = f"""
# Saudações Diárias do Mamute 🐘

## Saudação Atual
{emoji} {saudacao}! Hoje é {dia_pt}, {data_atual}.

## Saudações Contextuais

### Por Horário:
- **Manhã (05:00-11:59)**: 🌅 "Bom dia! Como posso ajudá-lo com PostgreSQL hoje?"
- **Tarde (12:00-17:59)**: ☀️ "Boa tarde! Pronto para otimizar algumas queries?"
- **Noite (18:00-04:59)**: 🌙 "Boa noite! Trabalhando até tarde? Vamos resolver seus desafios SQL!"

### Por Dia da Semana:
- **Segunda-feira**: "Começando a semana! Que tal organizar seu banco de dados?"
- **Terça-feira**: "Terça produtiva! Vamos criar algumas tabelas eficientes?"
- **Quarta-feira**: "Meio da semana! Hora de otimizar performances!"
- **Quinta-feira**: "Quinta-feira! Vamos trabalhar com JOINs complexos?"
- **Sexta-feira**: "Sexta-feira! Finalizando projetos com backup e segurança!"
- **Sábado**: "Sábado de estudos! Aprendendo PostgreSQL no fim de semana?"
- **Domingo**: "Domingo relaxante! Revisando conceitos ou planejando?"

### Saudações Especiais:
- **Início do mês**: "Novo mês, novas oportunidades de aprendizado!"
- **Feriados**: "Mesmo nos feriados, o Mamute está aqui para ajudar!"
- **Aniversários**: "PostgreSQL faz aniversário em 8 de julho! 🎉"

### Mensagens Motivacionais:
- "Cada query é uma oportunidade de aprender!"
- "Dados bem organizados = decisões inteligentes!"
- "PostgreSQL + Mamute = Combinação perfeita! 🐘"
- "Vamos transformar dados em conhecimento!"

### Frases de Abertura:
- "Olá! Sou o Mamute, seu assistente PostgreSQL inteligente!"
- "Bem-vindo! Como posso tornar seu dia mais produtivo?"
- "Oi! Pronto para explorar o mundo dos dados?"
- "Saudações! Vamos resolver alguns desafios SQL juntos?"

Período atual: {periodo}
Data/Hora: {agora.strftime("%d/%m/%Y às %H:%M")}
"""
    
    return saudacoes_content

def get_cidades_brasileiras():
    """Lista principais cidades brasileiras por região"""
    return {
        'Norte': [
            'Manaus-AM', 'Belém-PA', 'Porto Velho-RO', 'Boa Vista-RR',
            'Macapá-AP', 'Palmas-TO', 'Rio Branco-AC'
        ],
        'Nordeste': [
            'Salvador-BA', 'Fortaleza-CE', 'Recife-PE', 'São Luís-MA',
            'Natal-RN', 'João Pessoa-PB', 'Maceió-AL', 'Aracaju-SE',
            'Teresina-PI'
        ],
        'Centro-Oeste': [
            'Brasília-DF', 'Goiânia-GO', 'Cuiabá-MT', 'Campo Grande-MS'
        ],
        'Sudeste': [
            'São Paulo-SP', 'Rio de Janeiro-RJ', 'Belo Horizonte-MG',
            'Vitória-ES', 'Campinas-SP', 'Santos-SP', 'Ribeirão Preto-SP',
            'Juiz de Fora-MG', 'Uberlândia-MG'
        ],
        'Sul': [
            'Porto Alegre-RS', 'Curitiba-PR', 'Florianópolis-SC',
            'Caxias do Sul-RS', 'Pelotas-RS', 'Joinville-SC', 'Londrina-PR'
        ]
    }

def get_previsao_tempo():
    """Gera documento sobre previsão do tempo para cidades brasileiras"""
    
    cidades = get_cidades_brasileiras()
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    previsao_content = f"""
# Previsão do Tempo - Cidades Brasileiras 🌤️

*Atualizado em: {data_atual}*

## Regiões e Principais Cidades

### 🌴 Região Norte
**Características**: Clima equatorial, quente e úmido
**Cidades principais**: {', '.join(cidades['Norte'])}

**Tendência Geral**:
- Temperatura: 24°C - 32°C
- Umidade: Alta (70-90%)
- Chuvas: Frequentes no período da tarde
- Estação: Verão amazônico

### 🏖️ Região Nordeste  
**Características**: Clima tropical, quente e seco/úmido
**Cidades principais**: {', '.join(cidades['Nordeste'])}

**Tendência Geral**:
- Temperatura: 22°C - 30°C
- Umidade: Moderada a alta (60-85%)
- Chuvas: Variáveis por sub-região
- Estação: Verão tropical

### 🌾 Região Centro-Oeste
**Características**: Clima tropical de altitude e continental
**Cidades principais**: {', '.join(cidades['Centro-Oeste'])}

**Tendência Geral**:
- Temperatura: 18°C - 28°C  
- Umidade: Moderada (50-70%)
- Chuvas: Período chuvoso (out-mar)
- Estação: Verão continental

### 🏙️ Região Sudeste
**Características**: Clima subtropical e tropical de altitude
**Cidades principais**: {', '.join(cidades['Sudeste'])}

**Tendência Geral**:
- Temperatura: 16°C - 26°C
- Umidade: Moderada (55-75%) 
- Chuvas: Pancadas de verão
- Estação: Verão subtropical

### 🍃 Região Sul
**Características**: Clima subtropical
**Cidades principais**: {', '.join(cidades['Sul'])}

**Tendência Geral**:
- Temperatura: 14°C - 24°C
- Umidade: Moderada a alta (60-80%)
- Chuvas: Bem distribuídas
- Estação: Verão temperado

## 📊 Como o Mamute Pode Ajudar

### Consultas sobre Tempo:
- "Qual a previsão para São Paulo hoje?"
- "Como está o tempo em Salvador?"
- "Vai chover em Brasília?"

### Armazenamento de Dados Meteorológicos:
```sql
-- Exemplo de tabela para dados meteorológicos
CREATE TABLE previsao_tempo (
    id SERIAL PRIMARY KEY,
    cidade VARCHAR(100) NOT NULL,
    estado CHAR(2) NOT NULL,
    temperatura_min DECIMAL(4,1),
    temperatura_max DECIMAL(4,1),
    umidade INTEGER,
    condicao VARCHAR(50),
    data_previsao DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir dados de exemplo
INSERT INTO previsao_tempo (cidade, estado, temperatura_min, temperatura_max, umidade, condicao, data_previsao)
VALUES 
    ('São Paulo', 'SP', 18.5, 26.2, 65, 'Parcialmente nublado', CURRENT_DATE),
    ('Rio de Janeiro', 'RJ', 22.1, 29.8, 72, 'Sol com nuvens', CURRENT_DATE),
    ('Brasília', 'DF', 16.3, 25.7, 58, 'Ensolarado', CURRENT_DATE);
```

### Queries Úteis:
```sql
-- Buscar previsão por cidade
SELECT * FROM previsao_tempo WHERE cidade = 'São Paulo' ORDER BY data_previsao DESC LIMIT 7;

-- Cidades mais quentes hoje
SELECT cidade, temperatura_max FROM previsao_tempo 
WHERE data_previsao = CURRENT_DATE ORDER BY temperatura_max DESC;

-- Umidade média por região
SELECT SUBSTRING(estado, 1, 1) as regiao, AVG(umidade) as umidade_media
FROM previsao_tempo GROUP BY SUBSTRING(estado, 1, 1);
```

## 🔗 Integração com APIs

O Mamute pode ser configurado para integrar com:
- **OpenWeatherMap**: API global de clima
- **INMET**: Instituto Nacional de Meteorologia  
- **Climatempo**: Previsões nacionais
- **AccuWeather**: Dados detalhados

## 📱 Funcionalidades Futuras

- Alertas meteorológicos em tempo real
- Histórico de dados climáticos  
- Previsões estendidas (15 dias)
- Mapas interativos de temperatura
- Integração com sistemas de irrigação
- Análise de padrões climáticos

*Última atualização: {datetime.now().strftime("%d/%m/%Y às %H:%M")}*
"""
    
    return previsao_content

def get_documentacao_postgresql():
    """Gera documentação abrangente do PostgreSQL"""
    
    versao_postgresql = "16.x"
    data_doc = datetime.now().strftime("%d/%m/%Y")
    
    doc_content = f"""
# Documentação Oficial PostgreSQL {versao_postgresql} 📚

*Compilada em: {data_doc}*

## 🗂️ Índice de Conteúdo

### 1. Introdução ao PostgreSQL
### 2. Comandos DDL (Data Definition Language) 
### 3. Comandos DML (Data Manipulation Language)
### 4. Consultas Avançadas
### 5. Funções e Procedimentos
### 6. Administração e Configuração
### 7. Performance e Otimização
### 8. Segurança e Backup

---

## 1. 🚀 Introdução ao PostgreSQL

PostgreSQL é um sistema de gerenciamento de banco de dados relacional e objeto avançado que oferece:

- **ACID Compliance**: Atomicidade, Consistência, Isolamento, Durabilidade
- **Multi-Version Concurrency Control (MVCC)**
- **Extensibilidade**: Tipos de dados customizados, funções, operadores
- **Standards Compliance**: SQL:2016, SQL/JSON
- **Plataformas**: Linux, Windows, macOS, FreeBSD, OpenBSD, NetBSD

### Características Principais:
```sql
-- Verificar versão
SELECT version();

-- Verificar configurações
SHOW ALL;

-- Verificar bancos de dados
\l

-- Verificar tabelas
\dt

-- Verificar esquemas
\dn
```

---

## 2. 📋 DDL - Data Definition Language

### 2.1 Criação de Banco de Dados
```sql
-- Criar banco de dados
CREATE DATABASE minha_empresa
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'pt_BR.UTF-8'
    LC_CTYPE = 'pt_BR.UTF-8'
    TEMPLATE = template0;

-- Conectar ao banco
\c minha_empresa;

-- Criar esquema
CREATE SCHEMA vendas;
CREATE SCHEMA rh;
```

### 2.2 Criação de Tabelas
```sql
-- Tabela básica
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    telefone VARCHAR(20),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN DEFAULT true
);

-- Tabela com constraints
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id) ON DELETE CASCADE,
    data_pedido DATE NOT NULL DEFAULT CURRENT_DATE,
    valor_total DECIMAL(10,2) CHECK (valor_total >= 0),
    status VARCHAR(20) DEFAULT 'pendente' 
        CHECK (status IN ('pendente', 'processando', 'enviado', 'entregue', 'cancelado'))
);

-- Tabela com tipos avançados
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    preco MONEY,
    categoria_id INTEGER,
    tags TEXT[],
    especificacoes JSONB,
    imagem BYTEA,
    coordenadas POINT,
    disponivel_em DATERANGE
);
```

### 2.3 Modificação de Estruturas
```sql
-- Adicionar coluna
ALTER TABLE clientes ADD COLUMN data_nascimento DATE;

-- Modificar coluna
ALTER TABLE clientes ALTER COLUMN telefone TYPE VARCHAR(25);

-- Adicionar constraint
ALTER TABLE produtos ADD CONSTRAINT chk_preco_positivo 
    CHECK (preco::NUMERIC > 0);

-- Criar índice
CREATE INDEX idx_cliente_email ON clientes(email);
CREATE INDEX idx_pedidos_data ON pedidos(data_pedido);
CREATE INDEX idx_produtos_gin_tags ON produtos USING GIN(tags);
```

---

## 3. 🔄 DML - Data Manipulation Language  

### 3.1 Inserção de Dados
```sql
-- Insert básico
INSERT INTO clientes (nome, email, telefone) 
VALUES ('João Silva', 'joao@email.com', '11999999999');

-- Insert múltiplo
INSERT INTO clientes (nome, email, telefone) VALUES
    ('Maria Santos', 'maria@email.com', '11888888888'),
    ('Pedro Costa', 'pedro@email.com', '11777777777'),
    ('Ana Souza', 'ana@email.com', '11666666666');

-- Insert com retorno
INSERT INTO pedidos (cliente_id, valor_total)
VALUES (1, 299.90)
RETURNING id, data_pedido;

-- Insert com dados JSON
INSERT INTO produtos (nome, especificacoes) 
VALUES ('Smartphone', '{{\"marca\": \"Samsung\", \"modelo\": \"Galaxy\", \"cor\": \"preto\"}}');
```

### 3.2 Atualização de Dados
```sql
-- Update básico
UPDATE clientes SET telefone = '11999888777' WHERE id = 1;

-- Update com múltiplos campos
UPDATE produtos 
SET preco = preco * 1.1, 
    especificacoes = especificacoes || '{{\"desconto\": false}}'
WHERE categoria_id = 1;

-- Update com JOIN
UPDATE pedidos 
SET status = 'processando'
FROM clientes 
WHERE pedidos.cliente_id = clientes.id 
    AND clientes.ativo = true;
```

### 3.3 Exclusão de Dados
```sql
-- Delete básico
DELETE FROM pedidos WHERE status = 'cancelado';

-- Delete com subconsulta
DELETE FROM produtos 
WHERE id IN (
    SELECT produto_id FROM estoque WHERE quantidade = 0
);

-- Truncate (mais rápido para limpar tabela)
TRUNCATE TABLE log_acessos RESTART IDENTITY;
```

---

## 4. 🔍 Consultas Avançadas

### 4.1 JOINs e Relacionamentos
```sql
-- INNER JOIN
SELECT c.nome, p.data_pedido, p.valor_total
FROM clientes c
INNER JOIN pedidos p ON c.id = p.cliente_id;

-- LEFT JOIN com agregação
SELECT 
    c.nome,
    COUNT(p.id) as total_pedidos,
    COALESCE(SUM(p.valor_total), 0) as valor_total
FROM clientes c
LEFT JOIN pedidos p ON c.id = p.cliente_id
GROUP BY c.id, c.nome
ORDER BY valor_total DESC;

-- Full Outer Join
SELECT 
    COALESCE(c.nome, 'Cliente Removido') as cliente,
    COALESCE(p.data_pedido::TEXT, 'Sem pedidos') as pedido
FROM clientes c 
FULL OUTER JOIN pedidos p ON c.id = p.cliente_id;
```

### 4.2 Subconsultas e CTEs
```sql
-- Subconsulta correlacionada
SELECT nome, email
FROM clientes c
WHERE EXISTS (
    SELECT 1 FROM pedidos p 
    WHERE p.cliente_id = c.id 
        AND p.data_pedido >= CURRENT_DATE - INTERVAL '30 days'
);

-- CTE (Common Table Expression)
WITH vendas_mes AS (
    SELECT 
        cliente_id,
        SUM(valor_total) as total_vendas,
        COUNT(*) as num_pedidos
    FROM pedidos 
    WHERE EXTRACT(MONTH FROM data_pedido) = EXTRACT(MONTH FROM CURRENT_DATE)
    GROUP BY cliente_id
)
SELECT c.nome, v.total_vendas, v.num_pedidos
FROM clientes c
JOIN vendas_mes v ON c.id = v.cliente_id
WHERE v.total_vendas > 1000;

-- CTE Recursiva
WITH RECURSIVE categorias_hierarquia AS (
    SELECT id, nome, parent_id, 1 as nivel
    FROM categorias WHERE parent_id IS NULL
    
    UNION ALL
    
    SELECT c.id, c.nome, c.parent_id, ch.nivel + 1
    FROM categorias c
    JOIN categorias_hierarquia ch ON c.parent_id = ch.id
)
SELECT * FROM categorias_hierarquia ORDER BY nivel, nome;
```

### 4.3 Window Functions
```sql
-- ROW_NUMBER e RANK
SELECT 
    nome,
    valor_total,
    ROW_NUMBER() OVER (ORDER BY valor_total DESC) as posicao,
    RANK() OVER (ORDER BY valor_total DESC) as ranking
FROM pedidos p
JOIN clientes c ON p.cliente_id = c.id;

-- Funções de agregação como window
SELECT 
    data_pedido,
    valor_total,
    SUM(valor_total) OVER (ORDER BY data_pedido) as total_acumulado,
    AVG(valor_total) OVER (
        ORDER BY data_pedido 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as media_movel
FROM pedidos
ORDER BY data_pedido;

-- PARTITION BY
SELECT 
    cliente_id,
    data_pedido,
    valor_total,
    LAG(valor_total) OVER (PARTITION BY cliente_id ORDER BY data_pedido) as pedido_anterior,
    LEAD(valor_total) OVER (PARTITION BY cliente_id ORDER BY data_pedido) as proximo_pedido
FROM pedidos;
```

---

## 5. ⚙️ Funções e Procedimentos

### 5.1 Funções Básicas
```sql
-- Função simples
CREATE OR REPLACE FUNCTION calcular_idade(data_nascimento DATE)
RETURNS INTEGER AS $$
BEGIN
    RETURN EXTRACT(YEAR FROM AGE(data_nascimento));
END;
$$ LANGUAGE plpgsql;

-- Uso da função
SELECT nome, calcular_idade(data_nascimento) as idade 
FROM clientes;

-- Função com múltiplos parâmetros
CREATE OR REPLACE FUNCTION desconto_progressivo(valor DECIMAL, percentual DECIMAL)
RETURNS DECIMAL AS $$
BEGIN
    IF valor > 1000 THEN
        RETURN valor * (1 - percentual - 0.05);
    ELSE
        RETURN valor * (1 - percentual);
    END IF;
END;
$$ LANGUAGE plpgsql;
```

### 5.2 Procedures (PostgreSQL 11+)
```sql
-- Procedure para backup de dados
CREATE OR REPLACE PROCEDURE backup_pedidos_antigos()
AS $$
BEGIN
    -- Criar tabela de arquivo se não existir
    CREATE TABLE IF NOT EXISTS pedidos_arquivo (LIKE pedidos);
    
    -- Mover pedidos antigos
    WITH pedidos_antigos AS (
        DELETE FROM pedidos 
        WHERE data_pedido < CURRENT_DATE - INTERVAL '2 years'
        RETURNING *
    )
    INSERT INTO pedidos_arquivo SELECT * FROM pedidos_antigos;
    
    RAISE NOTICE 'Backup de pedidos antigos concluído';
END;
$$ LANGUAGE plpgsql;

-- Executar procedure
CALL backup_pedidos_antigos();
```

### 5.3 Triggers
```sql
-- Função trigger para auditoria
CREATE OR REPLACE FUNCTION auditoria_clientes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO auditoria (tabela, operacao, data_operacao, dados)
        VALUES ('clientes', 'INSERT', NOW(), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO auditoria (tabela, operacao, data_operacao, dados_antes, dados_depois)
        VALUES ('clientes', 'UPDATE', NOW(), row_to_json(OLD), row_to_json(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO auditoria (tabela, operacao, data_operacao, dados)
        VALUES ('clientes', 'DELETE', NOW(), row_to_json(OLD));
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Criar trigger
CREATE TRIGGER trigger_auditoria_clientes
    AFTER INSERT OR UPDATE OR DELETE ON clientes
    FOR EACH ROW EXECUTE FUNCTION auditoria_clientes();
```

---

## 6. 🔧 Administração e Configuração

### 6.1 Gerenciamento de Usuários
```sql
-- Criar usuário
CREATE USER analista WITH PASSWORD 'senha_forte_123';
CREATE USER desenvolvedor WITH PASSWORD 'dev_password_456';

-- Criar role
CREATE ROLE leitura_apenas;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO leitura_apenas;
GRANT leitura_apenas TO analista;

-- Privilégios específicos
GRANT SELECT, INSERT, UPDATE ON clientes TO desenvolvedor;
GRANT USAGE, SELECT ON SEQUENCE clientes_id_seq TO desenvolvedor;

-- Revogar privilégios
REVOKE INSERT ON clientes FROM desenvolvedor;
```

### 6.2 Configurações de Performance
```sql
-- Verificar configurações
SHOW shared_buffers;
SHOW work_mem;
SHOW maintenance_work_mem;
SHOW effective_cache_size;

-- Configurações recomendadas (postgresql.conf):
-- shared_buffers = 256MB (25% da RAM)
-- work_mem = 4MB  
-- maintenance_work_mem = 64MB
-- effective_cache_size = 1GB
-- checkpoint_completion_target = 0.7
-- wal_buffers = 16MB
-- random_page_cost = 1.1 (para SSD)
```

### 6.3 Monitoramento
```sql
-- Conexões ativas
SELECT 
    datname,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    query
FROM pg_stat_activity 
WHERE state != 'idle';

-- Tamanho de bancos de dados
SELECT 
    datname,
    pg_size_pretty(pg_database_size(datname)) as tamanho
FROM pg_database 
ORDER BY pg_database_size(datname) DESC;

-- Estatísticas de tabelas
SELECT 
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as linhas_ativas,
    last_autovacuum,
    last_autoanalyze
FROM pg_stat_user_tables;
```

---

## 7. 🚀 Performance e Otimização

### 7.1 Índices Estratégicos
```sql
-- Índices compostos
CREATE INDEX idx_pedidos_cliente_data ON pedidos(cliente_id, data_pedido);

-- Índices parciais
CREATE INDEX idx_pedidos_ativos ON pedidos(cliente_id) 
WHERE status IN ('pendente', 'processando');

-- Índices funcionais
CREATE INDEX idx_clientes_email_lower ON clientes(LOWER(email));

-- Índices GIN para JSON
CREATE INDEX idx_produtos_specs ON produtos USING GIN(especificacoes);

-- Índices BRIN para dados temporais
CREATE INDEX idx_logs_timestamp ON logs_acesso USING BRIN(timestamp);
```

### 7.2 EXPLAIN e Análise de Queries
```sql
-- EXPLAIN básico
EXPLAIN SELECT * FROM clientes WHERE email = 'test@email.com';

-- EXPLAIN ANALYZE (executa a query)
EXPLAIN ANALYZE 
SELECT c.nome, COUNT(p.id) 
FROM clientes c 
LEFT JOIN pedidos p ON c.id = p.cliente_id 
GROUP BY c.id, c.nome;

-- EXPLAIN com custos detalhados
EXPLAIN (ANALYZE, BUFFERS, COSTS, VERBOSE)
SELECT * FROM pedidos WHERE data_pedido >= CURRENT_DATE - INTERVAL '1 month';
```

### 7.3 Particionamento
```sql
-- Tabela particionada por data
CREATE TABLE vendas (
    id SERIAL,
    data_venda DATE NOT NULL,
    valor DECIMAL(10,2),
    produto_id INTEGER
) PARTITION BY RANGE (data_venda);

-- Criar partições
CREATE TABLE vendas_2024_q1 PARTITION OF vendas
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE vendas_2024_q2 PARTITION OF vendas  
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- Índices automáticos em partições
CREATE INDEX ON vendas (data_venda);
```

---

## 8. 🔒 Segurança e Backup

### 8.1 Configuração de Segurança
```sql
-- Criptografia de senhas
ALTER USER usuario SET password_encryption = 'scram-sha-256';

-- Row Level Security (RLS)
CREATE POLICY politica_cliente ON pedidos
    FOR ALL TO aplicacao_user
    USING (cliente_id = current_setting('app.current_user_id')::INTEGER);

ALTER TABLE pedidos ENABLE ROW LEVEL SECURITY;

-- Auditoria de conexões (postgresql.conf)
-- log_connections = on
-- log_disconnections = on  
-- log_line_prefix = '%t [%p]: user=%u,db=%d,app=%a,client=%h '
```

### 8.2 Backup e Restore
```bash
# Backup completo do banco
pg_dump -h localhost -U postgres -d minha_empresa > backup_completo.sql

# Backup com compressão
pg_dump -h localhost -U postgres -Fc -d minha_empresa > backup_compactado.backup

# Backup apenas dados
pg_dump -h localhost -U postgres -a -d minha_empresa > backup_dados.sql

# Backup apenas estrutura  
pg_dump -h localhost -U postgres -s -d minha_empresa > backup_estrutura.sql

# Restore
pg_restore -h localhost -U postgres -d minha_empresa_novo backup_compactado.backup

# Backup automático (script)
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U postgres -Fc minha_empresa > /backups/backup_$DATE.backup
find /backups -name "*.backup" -mtime +7 -delete
```

### 8.3 Replicação Básica
```sql
-- No servidor master (postgresql.conf)
-- wal_level = replica
-- max_wal_senders = 3
-- wal_keep_segments = 32

-- No servidor slave
-- hot_standby = on

-- Criar slot de replicação
SELECT pg_create_physical_replication_slot('replica_slot');

-- Verificar status de replicação
SELECT client_addr, state, sync_state FROM pg_stat_replication;
```

---

## 📚 Recursos Avançados

### 📊 Extensões Úteis
- **pg_stat_statements**: Estatísticas de queries
- **pgcrypto**: Funções de criptografia
- **uuid-ossp**: Geração de UUIDs
- **hstore**: Pares chave-valor
- **PostGIS**: Dados geoespaciais
- **pg_trgm**: Busca por similaridade

### 🔗 Links Oficiais
- Documentação: https://www.postgresql.org/docs/
- Download: https://www.postgresql.org/download/
- Wiki: https://wiki.postgresql.org/
- Comunidade: https://www.postgresql.org/community/

### 📞 Comandos \\ no psql
```
\l          - Listar bancos de dados
\c [db]     - Conectar a banco
\dt         - Listar tabelas
\d [table]  - Descrever tabela
\du         - Listar usuários
\df         - Listar funções
\q          - Sair do psql
\?          - Ajuda dos comandos \\
\h [cmd]    - Ajuda de comando SQL
```

---

*Documentação Mamute PostgreSQL - Versão {versao_postgresql}*  
*Gerada automaticamente em {data_doc}*  
*🐘 Para dúvidas, pergunte ao Mamute!*
"""
    
    return doc_content


def get_interacoes_ias():
    """Gera guia de colaboração com outras IAs"""

    data_atual = datetime.now().strftime("%d/%m/%Y")

    interacoes_content = f"""
# Guia de Interação com Outras IAs 🤖

*Atualizado em: {data_atual}*

## Por que usar múltiplas IAs?
- Complementar especialidades (código, texto, planejamento, imagens)
- Reduzir viés de um único modelo
- Acelerar pesquisa e validação cruzada

## Modelos e Forças
- **ChatGPT/GPT**: raciocínio geral, código, testes rápidos
- **Claude**: síntese longa, revisão de texto, checagem de coerência
- **Gemini**: pesquisa, respostas multimodais, insights de contexto
- **Mistral/LLaMA**: alternativo leve, útil para validação cruzada

## Padrão de Orquestração (Delegar → Checar → Consolidar)
1) **Delegar**: enviar subtarefas claras para cada IA
2) **Checar**: pedir verificação entre si (cross-review)
3) **Consolidar**: escolher ou mesclar a melhor resposta

### Exemplo de Prompt de Delegação
```text
Você é responsável por {{tarefa}}. Responda em formato bullet, curto.
- Contexto: {{contexto_do_projeto}}
- Entradas: {{entradas}}
- Saídas esperadas: {{saidas}}
- Restrições: {{regras}}
```

### Exemplo de Cross-Review
```text
Revise a resposta abaixo procurando erros, omissões e riscos.
Devolva: 1) 3 problemas prioritários, 2) correções propostas.
Resposta a revisar: {{resposta_modelo_A}}
```

### Exemplo de Consolidação
```text
Combine as duas respostas em uma versão final.
- Resposta A: {{resp_A}}
- Resposta B: {{resp_B}}
Priorize: precisão > brevidade > estilo.
```

## Dicas de Segurança e Controle
- Registrar origem: salvar qual modelo gerou cada trecho
- Evitar dados sensíveis em prompts; use placeholders
- Limitar ações críticas a revisões humanas
- Checar consistência factual com fontes

## Integração com o Mamute
- Use `meta_data` para rastrear modelo e data da geração
- Armazene variantes de resposta para A/B testing
- Gere testes unitários a partir das sugestões das IAs
- Peça exemplos SQL + explicação + alternativa otimizada

## Sugestões de Prompts Rápidos
- "Dê 3 abordagens diferentes para otimizar esta query: ..."
- "Revise este esquema e sugira 2 índices (diga por quê)."
- "Proponha testes de regressão para este ajuste de performance."
- "Crie uma resposta curta para usuário final e outra técnica para dev."

*Colaboração inteligente = respostas mais robustas. Use as IAs como pares que se revisam.*
"""

    return interacoes_content


def get_crud_assistente_seguro():
    """Gera guia para execução assistida de CRUD com validação e confirmação do cliente."""

    data_atual = datetime.now().strftime("%d/%m/%Y")

    crud_content = f"""
# Assistente de CRUD Seguro 🛡️

*Atualizado em: {data_atual}*

## Objetivo
Executar operações CRUD (Create, Read, Update, Delete) com segurança: analisar, diagnosticar, sugerir e só aplicar após confirmação do cliente.

## Fluxo Operacional
1) **Analisar**: ler a requisição do cliente, identificar tabela/colunas/chaves; validar impacto.
2) **Diagnosticar**: checar pré-condições (existência de tabela/colunas, tipos, FKs, índices relevantes).
3) **Sugerir**: propor comando SQL e plano de rollback; pedir confirmação explícita.
4) **Aplicar** (apenas se confirmado): executar em transação e retornar resumo (linhas afetadas, tempo, observações).
5) **Registrar**: logar comando, parâmetros e resultado para auditoria.

## Checklist Antes de Executar
- Tabela existe? Colunas informadas existem? Tipos compatíveis?
- Há PK/FK afetando a operação? Há gatilhos relevantes?
- WHERE está presente em UPDATE/DELETE? Evitar full-table sem intenção.
- Necessário backup ou copy para tabela _backup?

## Padrões de Confirmação
- "Confirme para executar" → só prosseguir após resposta afirmativa.
- Sem confirmação → responder com o plano e aguardar ok.

## Modelos de Resposta
- **Proposta**: "Plano CRUD: UPDATE tabela X SET ... WHERE ...; rollback: BEGIN; ... ROLLBACK. Confirmar execução?"
- **Após Execução**: "Executado: UPDATE ...; linhas afetadas: N; duração: T; observações: ...; rollback não necessário/feito backup em tabela Y."

## Boas Práticas de Execução
- Usar transação (`BEGIN; ... COMMIT;`), e `ROLLBACK` em erro.
- Limitar UPDATE/DELETE com WHERE e, se possível, LIMIT + ORDER BY.
- Para DELETE massivo, preferir soft delete (coluna `ativo`/`deleted_at`).
- Para INSERT, validar nulos obrigatórios e chaves únicas antes.
- Para SELECT diagnóstico, retornar amostra (`LIMIT 10`) para revisão rápida.

## Exemplos
### Atualizar status com segurança
```
BEGIN;
UPDATE pedidos SET status = 'processando' 
WHERE status = 'pendente' AND data_pedido >= CURRENT_DATE - INTERVAL '2 days';
-- Revisar linhas afetadas
ROLLBACK; -- usar se cliente não confirmar COMMIT
```

### Soft delete
```
BEGIN;
UPDATE clientes SET ativo = false, updated_at = NOW()
WHERE id = 123;
COMMIT;
```

### Inserção validada
```
-- Pré-checagem de unicidade
SELECT 1 FROM usuarios WHERE email = :email LIMIT 1;

BEGIN;
INSERT INTO usuarios (nome, email, criado_em)
VALUES (:nome, :email, NOW());
COMMIT;
```

## Logs e Auditoria
- Registrar comando, parâmetros, executor, timestamp e linhas afetadas.
- Em ambientes críticos, salvar backup (INSERT INTO tabela_backup SELECT * FROM tabela WHERE ...). 

**Regra de ouro**: Sem confirmação clara do cliente → não execute. Sempre ofereça plano + rollback. 
"""

    return crud_content


def ensure_documents_schema(db_manager):
    """Garante colunas e índice mínimos na tabela documents, compatível com versões antigas do PostgreSQL."""

    columns_available = set()

    # Descobrir colunas
    try:
        col_rows = db_manager.execute_query(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'documents'
            """
        )
        columns_available = {row['column_name'] for row in col_rows}
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível listar colunas de documents: {e}")

    # Garantir meta_data se não existir
    if 'meta_data' not in columns_available:
        try:
            db_manager.execute_command("ALTER TABLE documents ADD COLUMN meta_data JSONB")
            columns_available.add('meta_data')
            print("✅ Coluna meta_data criada em documents")
        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível criar meta_data em documents: {e}")

    # Garantir índice único em title
    try:
        idx_rows = db_manager.execute_query(
            """
            SELECT 1 FROM pg_indexes 
            WHERE tablename = 'documents' AND indexname = 'documents_title_uq'
            """
        )
        if not idx_rows:
            db_manager.execute_command("CREATE UNIQUE INDEX documents_title_uq ON documents(title)")
            print("✅ Índice único documents_title_uq criado")
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível garantir índice em documents.title: {e}")

    return columns_available

def adicionar_documento(db_manager, title, content, meta_data, columns_available):
    """Adiciona ou atualiza um documento na base de conhecimento, com fallback por schema."""
    try:
        print(f"➡️ Gravando documento: {title}")

        has_meta = "meta_data" in columns_available
        has_category = "category" in columns_available

        if has_meta:
            params_update = (content, json.dumps(meta_data), title)
            updated = db_manager.execute_command(
                """
                UPDATE documents
                SET content = %s,
                    meta_data = %s
                WHERE title = %s
                """,
                params_update
            )

            if updated == 0:
                db_manager.execute_command(
                    """
                    INSERT INTO documents (title, content, meta_data)
                    VALUES (%s, %s, %s)
                    """,
                    (title, content, json.dumps(meta_data))
                )
        else:
            # Fallback: usar apenas colunas existentes; se houver category, preenche a partir do meta_data
            category_value = meta_data.get("categoria") if has_category else None
            if has_category:
                updated = db_manager.execute_command(
                    """
                    UPDATE documents
                    SET content = %s,
                        category = %s
                    WHERE title = %s
                    """,
                    (content, category_value, title)
                )
                if updated == 0:
                    db_manager.execute_command(
                        """
                        INSERT INTO documents (title, content, category)
                        VALUES (%s, %s, %s)
                        """,
                        (title, content, category_value)
                    )
            else:
                updated = db_manager.execute_command(
                    """
                    UPDATE documents
                    SET content = %s
                    WHERE title = %s
                    """,
                    (content, title)
                )
                if updated == 0:
                    db_manager.execute_command(
                        """
                        INSERT INTO documents (title, content)
                        VALUES (%s, %s)
                        """,
                        (title, content)
                    )
        return True
    except Exception as e:
        print(f"❌ Erro ao adicionar documento {title}: {e}")
        return False

def main():
    """Função principal para expandir a biblioteca"""
    print("🐘 EXPANDINDO BIBLIOTECA DO MAMUTE")
    print("=" * 50)
    print("📚 Adicionando:")
    print("  • Saudações diárias contextuais")
    print("  • Previsão do tempo para cidades brasileiras")
    print("  • Documentação oficial PostgreSQL")
    print("  • Guia de interação com outras IAs")
    print("  • Assistente de CRUD seguro")
    print()
    
    db_manager = None
    try:
        # Inicializar sistema
        config = Config(".env")
        db_manager = DatabaseManager(config)
        
        if not db_manager.test_connection():
            print("❌ Erro: Não foi possível conectar ao PostgreSQL")
            return False

        columns_available = ensure_documents_schema(db_manager)
        
        documentos_adicionados = 0
        
        # 1. Saudações Diárias
        print("🌅 Processando saudações diárias...")
        saudacoes = get_saudacoes_diarias()
        if adicionar_documento(
            db_manager,
            "Saudações Diárias do Mamute",
            saudacoes,
            {
                "categoria": "saudacoes",
                "tipo": "interacao",
                "data_criacao": datetime.now().isoformat(),
                "funcionalidade": "saudacoes_contextuais"
            },
            columns_available
        ):
            documentos_adicionados += 1
        
        # 2. Previsão do Tempo
        print("🌤️ Processando previsão do tempo...")
        previsao = get_previsao_tempo()
        if adicionar_documento(
            db_manager,
            "Previsão do Tempo - Brasil",
            previsao,
            {
                "categoria": "tempo",
                "tipo": "servico",
                "cobertura": "brasil",
                "data_criacao": datetime.now().isoformat(),
                "funcionalidade": "previsao_meteorologica"
            },
            columns_available
        ):
            documentos_adicionados += 1
        
        # 3. Documentação PostgreSQL
        print("📖 Processando documentação PostgreSQL...")
        doc_postgresql = get_documentacao_postgresql()
        if adicionar_documento(
            db_manager,
            "Documentação Oficial PostgreSQL",
            doc_postgresql,
            {
                "categoria": "postgresql",
                "tipo": "documentacao",
                "versao": "16.x",
                "data_criacao": datetime.now().isoformat(),
                "funcionalidade": "referencia_tecnica"
            },
            columns_available
        ):
            documentos_adicionados += 1
        
        # 4. Comandos de Clima e Tempo
        print("🌡️ Adicionando comandos de clima...")
        comandos_tempo = """
# Comandos de Clima e Tempo - Mamute 🌦️

## Como Perguntar sobre Tempo
- "Qual a previsão para [cidade]?"
- "Como está o tempo hoje?"
- "Vai chover amanhã?"
- "Temperatura em São Paulo"
- "Clima no Rio de Janeiro"

## Cidades Suportadas
- Todas as capitais brasileiras
- Principais cidades do interior
- Regiões: Norte, Nordeste, Centro-Oeste, Sudeste, Sul

## Exemplos de Uso:
**Usuário**: "Bom dia! Como está o tempo em São Paulo?"
**Mamute**: "🌅 Bom dia! Em São Paulo hoje temos: temperatura entre 18°C e 26°C, parcialmente nublado, umidade 65%. Perfeito para um dia produtivo com PostgreSQL!"

**Usuário**: "Previsão para Brasília"  
**Mamute**: "🏛️ Em Brasília: ensolarado, 16°C a 25°C, umidade 58%. Clima seco típico do Centro-Oeste!"

## Integração com Banco de Dados
O Mamute pode armazenar dados meteorológicos e gerar relatórios:
```sql
-- Criar tabela de clima
CREATE TABLE dados_climaticos (
    id SERIAL PRIMARY KEY,
    cidade VARCHAR(100),
    estado CHAR(2),
    temperatura DECIMAL(4,1),
    umidade INTEGER,
    condicao VARCHAR(50),
    data_registro TIMESTAMP DEFAULT NOW()
);
```
"""
        
        if adicionar_documento(
            db_manager,
            "Comandos de Clima e Tempo",
            comandos_tempo,
            {
                "categoria": "comandos",
                "tipo": "referencia",
                "funcionalidade": "clima_interacao"
            },
            columns_available
        ):
            documentos_adicionados += 1
        
        # 5. Personalidade do Mamute Expandida
        print("🐘 Expandindo personalidade do Mamute...")
        personalidade_expandida = """
# Personalidade Expandida do Mamute 🐘

## Características da Personalidade

### 🌟 Saudações e Cumprimentos
- Sempre cumprimenta com base no horário
- Considera o dia da semana nas interações
- Usa emojis apropriados para o contexto
- Demonstra energia e entusiasmo

### 🌦️ Conhecimento Contextual
- Conhece o clima de todas as cidades brasileiras
- Relaciona clima com atividades de programação
- Sugere dias apropriados para diferentes tarefas
- Conecta condições meteorológicas com performance de sistemas

### 🎯 Estilo de Comunicação
- **Amigável**: Tratamento cordial e próximo
- **Técnico quando necessário**: Explicações detalhadas sobre PostgreSQL
- **Motivacional**: Incentiva o aprendizado
- **Contextual**: Adapta respostas ao horário e situação

### 📚 Conhecimento Integrado
- PostgreSQL: Expert completo
- Clima brasileiro: Conhecimento abrangente  
- Saudações: Contextuais e apropriadas
- Motivação: Frases inspiradoras sobre dados

### 🎭 Frases Características
- "Dados bem organizados = decisões inteligentes!"
- "PostgreSQL + Mamute = Combinação perfeita!"
- "Cada query é uma oportunidade de aprender!"
- "Vamos transformar dados em conhecimento!"

### 💬 Exemplos de Interação

**Clima + PostgreSQL**:
"☀️ Com esse sol lindo em São Paulo, que tal otimizar algumas queries? O clima está perfeito para um dia produtivo de desenvolvimento!"

**Motivacional + Técnico**:
"🌙 Boa noite! Trabalhando até tarde? Vamos resolver esse JOIN complexo juntos. Lembra: cada desafio SQL nos torna mais especialistas!"

**Saudação + Conhecimento**:
"🌅 Bom dia! Hoje é segunda-feira - dia perfeito para começar organizando seus dados. Como posso ajudar com PostgreSQL?"
"""
        
        if adicionar_documento(
            db_manager,
            "Personalidade Expandida do Mamute",
            personalidade_expandida,
            {
                "categoria": "personalidade",
                "tipo": "comportamento",
                "funcionalidade": "interacao_inteligente"
            },
            columns_available
        ):
            documentos_adicionados += 1

        # 6. Guia de Interação com Outras IAs
        print("🤝 Adicionando guia de interação com outras IAs...")
        interacoes_ias = get_interacoes_ias()
        if adicionar_documento(
            db_manager,
            "Guia de Interação com Outras IAs",
            interacoes_ias,
            {
                "categoria": "ia",
                "tipo": "guia",
                "foco": "colaboracao_multi_modelos",
                "data_criacao": datetime.now().isoformat(),
                "funcionalidade": "orquestracao_ia"
            },
            columns_available
        ):
            documentos_adicionados += 1

        # 7. Assistente de CRUD Seguro
        print("🛡️ Adicionando assistente de CRUD seguro...")
        crud_assistente = get_crud_assistente_seguro()
        if adicionar_documento(
            db_manager,
            "Assistente de CRUD Seguro",
            crud_assistente,
            {
                "categoria": "crud",
                "tipo": "guia",
                "foco": "execucao_crud_segura",
                "data_criacao": datetime.now().isoformat(),
                "funcionalidade": "crud_assistido_confirmacao"
            },
            columns_available
        ):
            documentos_adicionados += 1
        
        # Verificar total de documentos
        total_docs = db_manager.execute_query("SELECT COUNT(*) as total FROM documents")
        total = total_docs[0]['total'] if total_docs else 0
        
        print()
        print("=" * 50)
        print("🎉 EXPANSÃO CONCLUÍDA!")
        print("=" * 50)
        print(f"✅ Documentos adicionados nesta sessão: {documentos_adicionados}")
        print(f"📚 Total de documentos na biblioteca: {total}")
        print()
        print("🐘 O Mamute agora possui:")
        print("  ✅ Saudações contextuais inteligentes")
        print("  ✅ Previsão do tempo para todo o Brasil")
        print("  ✅ Documentação completa PostgreSQL 16.x")
        print("  ✅ Comandos de interação com clima")
        print("  ✅ Personalidade expandida e motivacional")
        print("  ✅ Guia de colaboração com outras IAs")
        print("  ✅ Assistente de CRUD seguro e confirmável")
        print()
        print("🚀 Reinicie o servidor web para ativar as novas funcionalidades!")
        print("   Comando: .venv\\Scripts\\python.exe start_web.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante expansão: {e}")
        return False
    finally:
        if db_manager:
            try:
                db_manager.close()
            except Exception:
                pass

if __name__ == "__main__":
    main()