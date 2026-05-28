"""Handlers de resposta para o fallback do Mamute.
Separados para manter o fallback_chat mais enxuto."""

from typing import Dict

def weather_response(message_lower: str) -> str:
    cidades_clima = {
        'são paulo': '☀️ São Paulo: 24°C, ensolarado, sem previsão de chuva',
        'rio de janeiro': '🌤️ Rio de Janeiro: 28°C, parcialmente nublado, 30% chance de chuva',
        'brasília': '⛅ Brasília: 22°C, nublado, possível chuva à tarde',
        'salvador': '☀️ Salvador: 30°C, ensolarado, tempo seco',
        'belo horizonte': '🌦️ Belo Horizonte: 20°C, chuva leve, tempo instável',
        'recife': '🌤️ Recife: 29°C, parcialmente nublado, brisa marítima',
        'porto alegre': '⛅ Porto Alegre: 18°C, nublado, frente fria aproximando',
        'fortaleza': '☀️ Fortaleza: 31°C, ensolarado, ventos alísios',
        'manaus': '🌦️ Manaus: 32°C, chuva tropical típica da região',
        'curitiba': '🌤️ Curitiba: 16°C, tempo fresco, típico do planalto'
    }

    cidade_encontrada = None
    for cidade, previsao in cidades_clima.items():
        if cidade.replace(' ', '') in message_lower.replace(' ', ''):
            cidade_encontrada = previsao
            break

    if cidade_encontrada:
        return (
            "🌤️ **Previsão do Tempo**\n\n"
            f"{cidade_encontrada}\n\n"
            "💡 Para outras cidades, pergunte: 'Como está o tempo em [cidade]?'"
        )

    return """🌤️ **Previsão do Tempo - Brasil**

📍 Principais cidades disponíveis:
• São Paulo: 24°C ☀️
• Rio de Janeiro: 28°C 🌤️
• Brasília: 22°C ⛅
• Salvador: 30°C ☀️
• Belo Horizonte: 20°C 🌦️
• Recife: 29°C 🌤️
• Porto Alegre: 18°C ⛅
• Fortaleza: 31°C ☀️
• Manaus: 32°C 🌦️
• Curitiba: 16°C 🌤️

Pergunte sobre uma cidade específica!"""


def sql_basics_response() -> str:
    return """📚 **PostgreSQL - Guia Rápido**

🔹 **Bancos e conexões**
```sql
-- Listar bancos
SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;

-- Conectar em outro banco (psql)
\c nome_do_banco
```

🔹 **Tabelas e esquema**
```sql
-- Listar tabelas do schema public
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Estrutura de tabela
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema='public' AND table_name='sua_tabela'
ORDER BY ordinal_position;
```

🔹 **Consultas básicas**
```sql
SELECT * FROM tabela;
SELECT nome, email FROM usuarios;
SELECT * FROM produtos WHERE preco > 100;
```

🔹 **Manipulação de dados**
```sql
INSERT INTO tabela (col1, col2) VALUES ('val1', 'val2');
UPDATE tabela SET coluna = 'valor' WHERE id = 1;
DELETE FROM tabela WHERE condição;
```

🔹 **Performance / índices**
```sql
-- Índices existentes
SELECT * FROM pg_indexes WHERE schemaname='public';

-- Tabelas grandes e sem índices
SELECT t.table_name, pg_size_pretty(pg_total_relation_size(c.oid)) AS size
FROM information_schema.tables t
JOIN pg_class c ON c.relname = t.table_name
WHERE t.table_schema='public'
ORDER BY pg_total_relation_size(c.oid) DESC
LIMIT 10;
```

❓ Precisa de algo específico? Pergunte sobre JOINs, índices ou otimização!"""


def create_db_response() -> str:
    return """🗄️ **Scripts para Criação de Banco de Dados PostgreSQL**

🔹 **1. Criar Banco de Dados:**
```sql
-- Criar banco simples
CREATE DATABASE minha_empresa;

-- Criar banco com configurações específicas
CREATE DATABASE sistema_vendas
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'pt_BR.UTF-8'
    LC_CTYPE = 'pt_BR.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = 100;

-- Conectar ao banco criado
\c sistema_vendas
```

🔹 **2. Criar Tabelas Básicas:**
```sql
-- Tabela de usuários
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de produtos
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10,2) NOT NULL,
    categoria_id INTEGER,
    estoque INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

🔹 **3. Criar Relacionamentos:**
```sql
-- Tabela de categorias
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT
);

-- Adicionar foreign key
ALTER TABLE produtos 
ADD CONSTRAINT fk_categoria 
FOREIGN KEY (categoria_id) REFERENCES categorias(id);
```

🔹 **4. Criar Índices:**
```sql
-- Índice no email para busca rápida
CREATE INDEX idx_usuarios_email ON usuarios(email);

-- Índice composto
CREATE INDEX idx_produtos_categoria_preco ON produtos(categoria_id, preco);
```

💡 **Precisa de algo específico? Posso ajudar com migrations, triggers e particionamento.**"""


def join_response() -> str:
    return """🔗 **JOINs no PostgreSQL (guia rápido)**

- INNER JOIN: somente correspondências
```sql
SELECT u.nome, p.nome
FROM usuarios u
INNER JOIN pedidos p ON p.usuario_id = u.id;
```

- LEFT JOIN: mantém registros da esquerda
```sql
SELECT u.nome, p.nome
FROM usuarios u
LEFT JOIN pedidos p ON p.usuario_id = u.id;
```

- FULL JOIN: combina tudo
```sql
SELECT * FROM a FULL JOIN b ON a.id = b.id;
```

Dica: garanta índices nas colunas usadas em JOIN para performance."""


def performance_response() -> str:
    return """🚀 **Performance & Índices**
- Crie índices para colunas usadas em filtros/JOINs
- Evite SELECT * em tabelas grandes
- Analise seq_scan vs idx_scan em pg_stat_user_tables
- Execute VACUUM ANALYZE regularmente
- Use EXPLAIN (ANALYZE, BUFFERS) para diagnosticar queries
"""


def functions_response() -> str:
    return """🧮 **Funções comuns**
- COUNT, SUM, AVG, MIN, MAX
```sql
SELECT COUNT(*) FROM pedidos;
SELECT AVG(total) FROM pedidos;
```
- Funções de data/hora
```sql
SELECT NOW(), CURRENT_DATE;
SELECT date_trunc('month', created_at) AS mes, COUNT(*) FROM pedidos GROUP BY 1;
```
- Agregação condicional
```sql
SELECT SUM(CASE WHEN status='pago' THEN total ELSE 0 END) FROM pedidos;
```
"""


def default_response(ai_name: str) -> str:
    return (
        f"🤖 Olá! Sou o {ai_name}. Posso ajudar com consultas SQL, otimização de PostgreSQL,"
        " backup, índices e análises rápidas. Pergunte algo específico ou peça um exemplo!"
    )


def about_response(ai_name: str) -> str:
    return f"Sou o {ai_name}, IA focada em PostgreSQL, performance e automações. Vamos otimizar seu banco juntos!"


def thanks_response() -> str:
    return "🙏 De nada! Fico à disposição para mais consultas ou otimizações."


def goodbye_response() -> str:
    return "👋 Até mais! Quando precisar de ajuda com PostgreSQL, é só chamar."
