"""
Script Simplificado para Expansão da Biblioteca do Mamute
"""

import sys
import os
import psycopg2
import json
from pathlib import Path

# Ajuste path para src
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
APPS_DIR = SRC_DIR / "apps"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

from src.database.connection import DatabaseManager
from src.utils.config import Config

def criar_saudacoes():
    """Cria documento de saudações contextuais"""
    return """
# Saudações Diárias do Mamute 🐘

## Saudações por Horário
- **Manhã (05:00-11:59)**: "Bom dia! Como posso ajudá-lo com PostgreSQL hoje?"
- **Tarde (12:00-17:59)**: "Boa tarde! Pronto para otimizar algumas queries?"
- **Noite (18:00-04:59)**: "Boa noite! Trabalhando até tarde? Vamos resolver seus desafios SQL!"

## Saudações por Dia da Semana
- **Segunda-feira**: "Começando a semana! Que tal organizar seu banco de dados?"
- **Terça-feira**: "Terça produtiva! Vamos criar algumas tabelas eficientes?"
- **Quarta-feira**: "Meio da semana! Hora de otimizar performances!"
- **Quinta-feira**: "Quinta-feira! Vamos trabalhar com JOINs complexos?"
- **Sexta-feira**: "Sexta-feira! Finalizando projetos com backup e segurança!"
- **Sábado**: "Sábado de estudos! Aprendendo PostgreSQL no fim de semana?"
- **Domingo**: "Domingo relaxante! Revisando conceitos ou planejando?"

## Frases Motivacionais
- "Cada query é uma oportunidade de aprender!"
- "Dados bem organizados = decisões inteligentes!"
- "PostgreSQL + Mamute = Combinação perfeita!"
- "Vamos transformar dados em conhecimento!"

## Cumprimentos de Abertura
- "Olá! Sou o Mamute, seu assistente PostgreSQL inteligente!"
- "Bem-vindo! Como posso tornar seu dia mais produtivo?"
- "Oi! Pronto para explorar o mundo dos dados?"
- "Saudações! Vamos resolver alguns desafios SQL juntos?"
"""

def criar_previsao_tempo():
    """Cria documento sobre clima brasileiro"""
    return """
# Previsão do Tempo - Brasil 🌤️

## Regiões e Principais Cidades

### 🌴 Norte: Manaus, Belém, Porto Velho, Boa Vista, Macapá, Palmas, Rio Branco
- Clima equatorial, quente e úmido
- Temperatura: 24°C - 32°C
- Chuvas frequentes à tarde

### 🏖️ Nordeste: Salvador, Fortaleza, Recife, São Luís, Natal, João Pessoa, Maceió, Aracaju
- Clima tropical, quente
- Temperatura: 22°C - 30°C
- Variação de chuvas por região

### 🌾 Centro-Oeste: Brasília, Goiânia, Cuiabá, Campo Grande
- Clima tropical continental
- Temperatura: 18°C - 28°C
- Estação seca e chuvosa bem definidas

### 🏙️ Sudeste: São Paulo, Rio de Janeiro, Belo Horizonte, Vitória
- Clima subtropical/tropical de altitude
- Temperatura: 16°C - 26°C
- Pancadas de chuva no verão

### 🍃 Sul: Porto Alegre, Curitiba, Florianópolis
- Clima subtropical
- Temperatura: 14°C - 24°C
- Chuvas bem distribuídas

## Como Perguntar sobre Tempo
- "Qual a previsão para São Paulo hoje?"
- "Como está o tempo em Salvador?"
- "Vai chover em Brasília?"
- "Temperatura em Curitiba"

## Integração com PostgreSQL
```sql
CREATE TABLE clima_brasil (
    id SERIAL PRIMARY KEY,
    cidade VARCHAR(100),
    estado CHAR(2),
    temperatura_min DECIMAL(4,1),
    temperatura_max DECIMAL(4,1),
    umidade INTEGER,
    condicao VARCHAR(50),
    data_previsao DATE
);
```
"""

def criar_doc_postgresql():
    """Cria documentação PostgreSQL"""
    return """
# Documentação PostgreSQL - Mamute 📚

## Comandos Básicos DDL
```sql
-- Criar banco
CREATE DATABASE minha_empresa;

-- Criar tabela
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Adicionar coluna
ALTER TABLE clientes ADD COLUMN telefone VARCHAR(20);

-- Criar índice
CREATE INDEX idx_cliente_email ON clientes(email);
```

## Comandos DML
```sql
-- Inserir dados
INSERT INTO clientes (nome, email) VALUES ('João', 'joao@email.com');

-- Atualizar dados
UPDATE clientes SET email = 'novo@email.com' WHERE id = 1;

-- Deletar dados
DELETE FROM clientes WHERE id = 1;
```

## Consultas Avançadas
```sql
-- JOIN
SELECT c.nome, p.data_pedido 
FROM clientes c 
JOIN pedidos p ON c.id = p.cliente_id;

-- Subconsulta
SELECT nome FROM clientes 
WHERE id IN (SELECT cliente_id FROM pedidos WHERE valor > 100);

-- Window Function
SELECT nome, valor, 
       ROW_NUMBER() OVER (ORDER BY valor DESC) as ranking
FROM vendas;
```

## Funções Úteis
```sql
-- Funções de data
SELECT CURRENT_DATE, CURRENT_TIME, NOW();

-- Funções de string
SELECT UPPER(nome), LOWER(email), LENGTH(nome) FROM clientes;

-- Funções de agregação
SELECT COUNT(*), SUM(valor), AVG(valor), MAX(valor), MIN(valor) FROM vendas;
```

## Administração
```sql
-- Ver conexões ativas
SELECT * FROM pg_stat_activity;

-- Tamanho do banco
SELECT pg_database_size('nome_banco');

-- Estatísticas de tabelas
SELECT * FROM pg_stat_user_tables;
```

## Tipos de Dados
- INTEGER, BIGINT, DECIMAL, NUMERIC
- VARCHAR(n), TEXT, CHAR(n)
- DATE, TIME, TIMESTAMP, INTERVAL
- BOOLEAN
- JSONB, ARRAY
- UUID, POINT, INET

## Índices e Performance
```sql
-- Índices básicos
CREATE INDEX ON tabela(coluna);

-- Índices compostos
CREATE INDEX ON tabela(col1, col2);

-- Índices parciais
CREATE INDEX ON tabela(coluna) WHERE condicao;

-- Analisar query
EXPLAIN ANALYZE SELECT * FROM tabela WHERE condicao;
```

## Backup e Restore
```bash
# Backup
pg_dump -h localhost -U postgres -d banco > backup.sql

# Restore
psql -h localhost -U postgres -d banco < backup.sql
```

## Comandos psql
```
\\l          - Listar bancos
\\c [db]     - Conectar a banco  
\\dt         - Listar tabelas
\\d [table]  - Descrever tabela
\\q          - Sair
```
"""

def adicionar_documento_simples(db_manager, titulo, conteudo, categoria):
    """Adiciona documento de forma simples"""
    try:
        meta_data = json.dumps({
            "categoria": categoria,
            "data_criacao": datetime.now().isoformat(),
            "tipo": "conhecimento"
        })
        
        # Verificar se existe
        resultado = db_manager.execute_query(
            "SELECT COUNT(*) as total FROM documents WHERE title = %s", 
            (titulo,)
        )
        
        existe = resultado and len(resultado) > 0 and resultado[0]['total'] > 0
        
        if existe:
            print(f"📝 Atualizando: {titulo}")
            db_manager.execute_query(
                "UPDATE documents SET content = %s, meta_data = %s WHERE title = %s",
                (conteudo, meta_data, titulo)
            )
        else:
            print(f"➕ Adicionando: {titulo}")
            db_manager.execute_query(
                "INSERT INTO documents (title, content, meta_data) VALUES (%s, %s, %s)",
                (titulo, conteudo, meta_data)
            )
        
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("🐘 EXPANDINDO BIBLIOTECA DO MAMUTE")
    print("=" * 50)
    
    try:
        # Conectar ao banco
        config = Config(".env")
        db_manager = DatabaseManager(config)
        
        if not db_manager.test_connection():
            print("❌ Erro de conexão com PostgreSQL")
            return False
        
        print("✅ Conectado ao PostgreSQL")
        
        contador = 0
        
        # 1. Saudações
        if adicionar_documento_simples(
            db_manager, 
            "Saudações Diárias do Mamute",
            criar_saudacoes(),
            "saudacoes"
        ):
            contador += 1
        
        # 2. Clima
        if adicionar_documento_simples(
            db_manager,
            "Previsão do Tempo Brasil",
            criar_previsao_tempo(), 
            "clima"
        ):
            contador += 1
        
        # 3. PostgreSQL
        if adicionar_documento_simples(
            db_manager,
            "Documentação PostgreSQL Completa",
            criar_doc_postgresql(),
            "postgresql"
        ):
            contador += 1
        
        # Contar total
        resultado = db_manager.execute_query("SELECT COUNT(*) as total FROM documents")
        total = resultado[0]['total'] if resultado and len(resultado) > 0 else 0
        
        print()
        print("=" * 50)
        print("🎉 EXPANSÃO CONCLUÍDA!")
        print("=" * 50)
        print(f"✅ Documentos processados: {contador}")
        print(f"📚 Total na biblioteca: {total}")
        print()
        print("🐘 Mamute agora possui:")
        print("  ✅ Saudações contextuais")
        print("  ✅ Previsão do tempo do Brasil")
        print("  ✅ Documentação PostgreSQL completa")
        print()
        print("🚀 Para usar, reinicie o servidor web!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

if __name__ == "__main__":
    main()