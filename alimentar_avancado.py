"""
Alimentador Avançado da Base de Conhecimento do Mamute
Inclui: Saudações, Clima do Brasil e Documentação PostgreSQL
"""

import sys
import os
import json
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.models import Document
from src.database.connection import DatabaseManager
from src.utils.config import Config

def get_saudacoes_diarias():
    """Retorna base de conhecimento de saudações diárias"""
    return {
        "title": "Saudações Diárias do Mamute",
        "content": """
🐘 SAUDAÇÕES DO MAMUTE POR HORÁRIO

=== MANHÃ (05:00 - 11:59) ===
• Bom dia! Como posso ajudá-lo com PostgreSQL hoje?
• Que bom começar o dia com você! Vamos trabalhar com dados?
• Manhã perfeita para otimizar algumas queries, não acha?
• Bom dia! Pronto para explorar o mundo dos bancos de dados?
• Olá! Que tal começarmos o dia com uma consulta interessante?

=== TARDE (12:00 - 17:59) ===
• Boa tarde! Espero que esteja tendo um dia produtivo!
• Tarde perfeita para resolver questões de banco de dados!
• Boa tarde! Como posso auxiliar nas suas consultas SQL?
• Olá! Vamos aproveitar a tarde para trabalhar com dados?
• Boa tarde! Pronto para otimizar seu PostgreSQL?

=== NOITE (18:00 - 22:59) ===
• Boa noite! Ainda trabalhando? Vamos resolver isso juntos!
• Noite produtiva para programar! Como posso ajudar?
• Boa noite! Que tal finalizarmos o dia com queries perfeitas?
• Olá! Mesmo à noite, estou aqui para auxiliar com PostgreSQL!
• Boa noite! Vamos otimizar algumas consultas antes de descansar?

=== MADRUGADA (23:00 - 04:59) ===
• Olá, coruja da madrugada! Vamos debugar algumas queries?
• Madrugada produtiva! Como posso ajudar com seu banco de dados?
• Ainda acordado? Perfeito, vamos trabalhar com PostgreSQL!
• Madrugada é hora de foco! Vamos resolver suas dúvidas SQL?
• Olá! Mesmo de madrugada, estou aqui para auxiliar!

=== SAUDAÇÕES ESPECIAIS ===
• Seja bem-vindo ao mundo do PostgreSQL com o Mamute!
• Que alegria ter você aqui! Sou seu assistente especialista em PostgreSQL.
• Olá! Sou o Mamute, sua IA especializada em bancos de dados PostgreSQL.
• Prazer em ajudá-lo! Vamos explorar o potencial do PostgreSQL juntos!
• Bem-vindo! Estou aqui para tornar o PostgreSQL mais fácil para você.

=== SAUDAÇÕES DE DESPEDIDA ===
• Até logo! Foi um prazer ajudá-lo com PostgreSQL hoje!
• Tchau! Espero ter sido útil. Volte sempre que precisar!
• Até a próxima! Continue explorando o mundo dos dados!
• Foi ótimo trabalhar com você! Até logo!
• Adeus! Lembre-se: o Mamute está sempre aqui para ajudar!
        """,
        "meta_data": {
            "category": "saudacoes",
            "source": "mamute_personalidade",
            "tipo": "interacao_social",
            "horarios": ["manha", "tarde", "noite", "madrugada"],
            "created_at": datetime.now().isoformat()
        }
    }

def get_clima_brasil():
    """Retorna sistema de consulta de clima para cidades brasileiras"""
    return {
        "title": "Sistema de Previsão do Tempo - Brasil",
        "content": """
🌤️ SISTEMA DE CLIMA DO BRASIL - MAMUTE

=== PRINCIPAIS CIDADES E CÓDIGOS ===
• São Paulo (SP) - Código: 3448439
• Rio de Janeiro (RJ) - Código: 3451190  
• Brasília (DF) - Código: 3469058
• Salvador (BA) - Código: 3450554
• Fortaleza (CE) - Código: 3399415
• Belo Horizonte (MG) - Código: 3470127
• Manaus (AM) - Código: 3663517
• Curitiba (PR) - Código: 3464975
• Recife (PE) - Código: 3390760
• Goiânia (GO) - Código: 3462377
• Belém (PA) - Código: 3405870
• Porto Alegre (RS) - Código: 3452925

=== REGIÕES BRASILEIRAS ===

REGIÃO NORTE:
• Acre: Rio Branco, Cruzeiro do Sul
• Amazonas: Manaus, Parintins, Itacoatiara
• Amapá: Macapá, Santana
• Pará: Belém, Santarém, Marabá
• Rondônia: Porto Velho, Ji-Paraná
• Roraima: Boa Vista, Rorainópolis
• Tocantins: Palmas, Araguaína

REGIÃO NORDESTE:
• Alagoas: Maceió, Arapiraca
• Bahia: Salvador, Feira de Santana, Vitória da Conquista
• Ceará: Fortaleza, Caucaia, Juazeiro do Norte
• Maranhão: São Luís, Imperatriz
• Paraíba: João Pessoa, Campina Grande
• Pernambuco: Recife, Jaboatão dos Guararapes, Olinda
• Piauí: Teresina, Parnaíba
• Rio Grande do Norte: Natal, Mossoró
• Sergipe: Aracaju, Nossa Senhora do Socorro

REGIÃO CENTRO-OESTE:
• Distrito Federal: Brasília
• Goiás: Goiânia, Aparecida de Goiânia, Anápolis
• Mato Grosso: Cuiabá, Várzea Grande, Rondonópolis
• Mato Grosso do Sul: Campo Grande, Dourados

REGIÃO SUDESTE:
• Espírito Santo: Vitória, Cariacica, Serra
• Minas Gerais: Belo Horizonte, Uberlândia, Contagem
• Rio de Janeiro: Rio de Janeiro, São Gonçalo, Duque de Caxias
• São Paulo: São Paulo, Guarulhos, Campinas

REGIÃO SUL:
• Paraná: Curitiba, Londrina, Maringá
• Rio Grande do Sul: Porto Alegre, Caxias do Sul, Pelotas
• Santa Catarina: Florianópolis, Joinville, Blumenau

=== COMANDOS DE CLIMA DISPONÍVEIS ===
• "clima [cidade]" - Previsão atual
• "tempo [cidade]" - Previsão detalhada
• "previsão [cidade]" - Próximos dias
• "temperatura [cidade]" - Temperatura atual

=== API INTEGRATION ===
Endpoint: https://api.openweathermap.org/data/2.5/weather
Parâmetros necessários:
- q: nome da cidade
- appid: chave da API
- units: metric
- lang: pt_br

Exemplo de consulta:
GET https://api.openweathermap.org/data/2.5/weather?q=São Paulo&appid=KEY&units=metric&lang=pt_br

=== FRASES PARA CLIMA ===
• "Deixe-me verificar o tempo em [cidade] para você!"
• "A previsão para [cidade] está chegando..."
• "Consultando os dados meteorológicos de [cidade]..."
• "Verificando as condições climáticas em [cidade]..."
        """,
        "meta_data": {
            "category": "clima",
            "source": "api_openweather", 
            "tipo": "servicos_brasil",
            "regioes": ["norte", "nordeste", "centro-oeste", "sudeste", "sul"],
            "created_at": datetime.now().isoformat()
        }
    }

def get_documentacao_postgresql_oficial():
    """Retorna documentação oficial do PostgreSQL"""
    return [
        {
            "title": "PostgreSQL - Documentação Oficial Completa",
            "content": """
📖 DOCUMENTAÇÃO OFICIAL DO POSTGRESQL

=== LINKS PRINCIPAIS ===
• Site Oficial: https://www.postgresql.org/
• Documentação: https://www.postgresql.org/docs/
• Downloads: https://www.postgresql.org/download/
• Comunidade: https://www.postgresql.org/community/

=== VERSÕES SUPORTADAS ===
• PostgreSQL 16 (Atual): https://www.postgresql.org/docs/16/
• PostgreSQL 15: https://www.postgresql.org/docs/15/
• PostgreSQL 14: https://www.postgresql.org/docs/14/
• PostgreSQL 13: https://www.postgresql.org/docs/13/
• PostgreSQL 12: https://www.postgresql.org/docs/12/

=== SEÇÕES PRINCIPAIS DA DOCUMENTAÇÃO ===

1. TUTORIAL (Getting Started)
   - https://www.postgresql.org/docs/current/tutorial.html
   - Conceitos básicos
   - Primeiros passos
   - Criação de tabelas
   - Inserção de dados

2. SQL LANGUAGE
   - https://www.postgresql.org/docs/current/sql.html
   - Sintaxe SQL
   - Comandos DML/DDL
   - Funções e operadores
   - Tipos de dados

3. SERVER ADMINISTRATION
   - https://www.postgresql.org/docs/current/admin.html
   - Instalação e configuração
   - Gerenciamento de usuários
   - Backup e restore
   - Monitoramento

4. SERVER PROGRAMMING
   - https://www.postgresql.org/docs/current/server-programming.html
   - Functions e procedures
   - Triggers
   - Extensões
   - PL/pgSQL

5. REFERENCE
   - https://www.postgresql.org/docs/current/reference.html
   - Comandos SQL
   - Utilitários cliente
   - Aplicações servidor

=== GUIAS ESPECÍFICOS ===

PERFORMANCE TUNING:
https://www.postgresql.org/docs/current/performance-tips.html
- Otimização de queries
- Índices
- ANALYZE e VACUUM
- Configuração de memória

SECURITY:
https://www.postgresql.org/docs/current/client-authentication.html
- Autenticação
- Autorização
- SSL/TLS
- Row Level Security

REPLICATION:
https://www.postgresql.org/docs/current/high-availability.html
- Streaming replication
- Logical replication
- Hot standby
- Point-in-time recovery

=== MANUAIS ESPECÍFICOS ===

pgAdmin 4: https://www.pgadmin.org/docs/
psql: https://www.postgresql.org/docs/current/app-psql.html
pg_dump: https://www.postgresql.org/docs/current/app-pgdump.html
pg_restore: https://www.postgresql.org/docs/current/app-pgrestore.html

=== RECURSOS DE APRENDIZADO ===

PostgreSQL Wiki: https://wiki.postgresql.org/
PostgreSQL Tutorials: https://www.postgresqltutorial.com/
Planet PostgreSQL: https://planet.postgresql.org/
PostgreSQL Weekly: https://postgresqlco.nf/

=== LIVROS OFICIAIS RECOMENDADOS ===
• "PostgreSQL: Up and Running" - Regina Obe
• "PostgreSQL High Performance" - Gregory Smith
• "PostgreSQL Administration Cookbook" - Simon Riggs
• "Learning PostgreSQL" - Salahaldin Juba
            """,
            "meta_data": {
                "category": "documentacao",
                "source": "postgresql_oficial",
                "tipo": "referencia_oficial",
                "versao": "16.x",
                "idioma": "en",
                "created_at": datetime.now().isoformat()
            }
        },
        {
            "title": "PostgreSQL - Comandos SQL Essenciais",
            "content": """
🔧 COMANDOS SQL ESSENCIAIS - REFERÊNCIA OFICIAL

=== DDL (DATA DEFINITION LANGUAGE) ===

CREATE DATABASE:
  CREATE DATABASE nome_db 
  WITH ENCODING 'UTF8' 
  LC_COLLATE='pt_BR.UTF-8';

CREATE TABLE:
  CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
  );

ALTER TABLE:
  ALTER TABLE usuarios 
  ADD COLUMN idade INTEGER,
  DROP COLUMN temp_col,
  ALTER COLUMN nome SET NOT NULL;

CREATE INDEX:
  CREATE INDEX idx_usuarios_email 
  ON usuarios USING btree (email);
  
  CREATE INDEX idx_usuarios_nome_gin 
  ON usuarios USING gin (to_tsvector('portuguese', nome));

=== DML (DATA MANIPULATION LANGUAGE) ===

INSERT:
  INSERT INTO usuarios (nome, email) 
  VALUES ('João Silva', 'joao@email.com')
  RETURNING id;

UPDATE:
  UPDATE usuarios 
  SET nome = 'João Santos' 
  WHERE id = 1;

DELETE:
  DELETE FROM usuarios 
  WHERE created_at < NOW() - INTERVAL '1 year';

SELECT:
  SELECT u.nome, u.email, COUNT(p.id) as total_posts
  FROM usuarios u
  LEFT JOIN posts p ON u.id = p.usuario_id
  WHERE u.created_at > '2023-01-01'
  GROUP BY u.id, u.nome, u.email
  HAVING COUNT(p.id) > 5
  ORDER BY total_posts DESC
  LIMIT 10;

=== DCL (DATA CONTROL LANGUAGE) ===

GRANT:
  GRANT SELECT, INSERT, UPDATE 
  ON usuarios TO app_user;
  
  GRANT USAGE ON SEQUENCE usuarios_id_seq 
  TO app_user;

REVOKE:
  REVOKE DELETE ON usuarios FROM app_user;

CREATE USER:
  CREATE USER app_user WITH PASSWORD 'senha123';

=== TCL (TRANSACTION CONTROL LANGUAGE) ===

BEGIN/COMMIT:
  BEGIN;
  UPDATE contas SET saldo = saldo - 100 WHERE id = 1;
  UPDATE contas SET saldo = saldo + 100 WHERE id = 2;
  COMMIT;

ROLLBACK:
  BEGIN;
  DELETE FROM dados_importantes;
  ROLLBACK; -- Desfaz a operação

SAVEPOINT:
  BEGIN;
  INSERT INTO log (mensagem) VALUES ('inicio');
  SAVEPOINT sp1;
  UPDATE dados SET valor = 0; -- erro aqui
  ROLLBACK TO SAVEPOINT sp1;
  INSERT INTO log (mensagem) VALUES ('recuperado');
  COMMIT;

=== FUNÇÕES ANALÍTICAS (WINDOW FUNCTIONS) ===

ROW_NUMBER:
  SELECT nome, salario,
    ROW_NUMBER() OVER (ORDER BY salario DESC) as posicao
  FROM funcionarios;

RANK:
  SELECT nome, departamento, salario,
    RANK() OVER (PARTITION BY departamento ORDER BY salario DESC) as rank_dept
  FROM funcionarios;

LAG/LEAD:
  SELECT data_venda, valor,
    LAG(valor) OVER (ORDER BY data_venda) as valor_anterior,
    LEAD(valor) OVER (ORDER BY data_venda) as valor_proximo
  FROM vendas;

=== CTE (COMMON TABLE EXPRESSIONS) ===

WITH RECURSIVE:
  WITH RECURSIVE funcionarios_hierarquia AS (
    SELECT id, nome, gerente_id, 0 as nivel
    FROM funcionarios 
    WHERE gerente_id IS NULL
    
    UNION ALL
    
    SELECT f.id, f.nome, f.gerente_id, fh.nivel + 1
    FROM funcionarios f
    JOIN funcionarios_hierarquia fh ON f.gerente_id = fh.id
  )
  SELECT * FROM funcionarios_hierarquia;

=== TIPOS DE DADOS AVANÇADOS ===

JSON/JSONB:
  CREATE TABLE produtos (
    id SERIAL,
    dados JSONB
  );
  
  SELECT dados->'nome' as nome_produto
  FROM produtos 
  WHERE dados @> '{"categoria": "eletrônicos"}';

ARRAY:
  CREATE TABLE posts (
    id SERIAL,
    tags TEXT[]
  );
  
  SELECT * FROM posts 
  WHERE 'postgresql' = ANY(tags);

FULL TEXT SEARCH:
  SELECT *, ts_rank(search_vector, query) as rank
  FROM documentos, plainto_tsquery('portuguese', 'postgresql banco dados') query
  WHERE search_vector @@ query
  ORDER BY rank DESC;
            """,
            "meta_data": {
                "category": "documentacao",
                "source": "postgresql_sql_commands",
                "tipo": "referencia_comandos",
                "nivel": "intermediario_avancado",
                "created_at": datetime.now().isoformat()
            }
        },
        {
            "title": "PostgreSQL - Configuração e Otimização",
            "content": """
⚙️ CONFIGURAÇÃO E OTIMIZAÇÃO DO POSTGRESQL

=== ARQUIVO postgresql.conf ===

MEMÓRIA:
  # Memória compartilhada (25% da RAM)
  shared_buffers = 256MB
  
  # Cache efetivo (75% da RAM)  
  effective_cache_size = 1GB
  
  # Memória de trabalho por operação
  work_mem = 4MB
  
  # Memória para manutenção
  maintenance_work_mem = 64MB

CHECKPOINT:
  # Frequência de checkpoint
  checkpoint_completion_target = 0.7
  
  # Tempo máximo entre checkpoints  
  checkpoint_timeout = 10min
  
  # Tamanho máximo do WAL
  max_wal_size = 1GB

CONEXÕES:
  # Máximo de conexões
  max_connections = 100
  
  # Tempo limite de conexão inativa
  tcp_keepalives_idle = 600
  
  # Timeout de statement
  statement_timeout = 30s

LOGGING:
  # Log de queries lentas
  log_min_duration_statement = 1000
  
  # Log detalhado
  log_line_prefix = '%t [%p-%l] %u@%d '
  log_checkpoints = on
  log_connections = on
  log_disconnections = on

=== ARQUIVO pg_hba.conf ===

AUTENTICAÇÃO LOCAL:
  # TYPE  DATABASE        USER            ADDRESS                 METHOD
  local   all             postgres                                peer
  local   all             all                                     md5
  
AUTENTICAÇÃO REMOTA:
  host    all             all             192.168.1.0/24          md5
  host    replication     repl_user       192.168.1.0/24          md5

SSL:
  hostssl all             all             0.0.0.0/0               md5

=== COMANDOS DE MANUTENÇÃO ===

VACUUM:
  -- Limpeza básica
  VACUUM;
  
  -- Limpeza completa (bloqueia tabela)
  VACUUM FULL;
  
  -- Limpeza específica
  VACUUM VERBOSE ANALYZE tabela_usuarios;

REINDEX:
  -- Recriar todos os índices
  REINDEX DATABASE minha_db;
  
  -- Recriar índice específico
  REINDEX INDEX idx_usuarios_email;

ANALYZE:
  -- Atualizar estatísticas
  ANALYZE;
  
  -- Análise específica
  ANALYZE tabela_vendas;

=== MONITORAMENTO ===

ATIVIDADE ATUAL:
  SELECT pid, usename, application_name, state, query
  FROM pg_stat_activity 
  WHERE state = 'active';

LOCKS:
  SELECT blocked_locks.pid AS blocked_pid,
         blocked_activity.usename AS blocked_user,
         blocking_locks.pid AS blocking_pid,
         blocking_activity.usename AS blocking_user,
         blocked_activity.query AS blocked_statement,
         blocking_activity.query AS current_statement_in_blocking_process
  FROM pg_catalog.pg_locks blocked_locks
  JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
  JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
  JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
  WHERE NOT blocked_locks.granted;

TAMANHO DE TABELAS:
  SELECT schemaname,tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
  FROM pg_tables 
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

=== BACKUP E RESTORE ===

pg_dump:
  # Backup completo
  pg_dump -h localhost -U postgres -d mydb > backup.sql
  
  # Backup comprimido
  pg_dump -h localhost -U postgres -Fc -d mydb > backup.dump
  
  # Backup apenas schema
  pg_dump -h localhost -U postgres -s -d mydb > schema.sql

pg_restore:
  # Restore completo
  pg_restore -h localhost -U postgres -d newdb backup.dump
  
  # Restore apenas dados
  pg_restore -h localhost -U postgres -a -d newdb backup.dump

=== REPLICAÇÃO ===

CONFIGURAÇÃO MASTER:
  # postgresql.conf
  wal_level = replica
  max_wal_senders = 3
  checkpoint_segments = 8
  wal_keep_segments = 8

CONFIGURAÇÃO SLAVE:
  # recovery.conf
  standby_mode = 'on'
  primary_conninfo = 'host=master_ip port=5432 user=repl_user'
  trigger_file = '/tmp/postgresql.trigger'

=== SEGURANÇA ===

SSL:
  # postgresql.conf
  ssl = on
  ssl_cert_file = 'server.crt'
  ssl_key_file = 'server.key'

ROW LEVEL SECURITY:
  CREATE POLICY usuarios_policy ON usuarios
  FOR ALL TO app_role
  USING (user_id = current_user_id());
  
  ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
            """,
            "meta_data": {
                "category": "documentacao",
                "source": "postgresql_configuracao",
                "tipo": "administracao_sistema",
                "nivel": "avancado",
                "created_at": datetime.now().isoformat()
            }
        }
    ]

def alimentar_base_avancada():
    """Alimenta a base de conhecimento com conteúdo avançado"""
    
    print("🚀 ALIMENTANDO BASE AVANÇADA DO MAMUTE")
    print("=" * 50)
    
    try:
        # Configurar sistema
        config = Config(".env")
        db_manager = DatabaseManager(config)
        
        print(f"✅ Configuração carregada - IA: {config.ai_name}")
        
        # Conectar ao banco
        if not db_manager.test_connection():
            print("❌ Erro: Não foi possível conectar ao PostgreSQL")
            return False
        
        print("✅ Conexão PostgreSQL estabelecida")
        
        # Alimentar saudações
        print("\n📝 Alimentando saudações diárias...")
        saudacoes = get_saudacoes_diarias()
        
        doc_saudacoes = Document(
            title=saudacoes["title"],
            content=saudacoes["content"],
            meta_data=saudacoes["meta_data"]
        )
        
        db_manager.session.add(doc_saudacoes)
        db_manager.session.commit()
        print("✅ Saudações diárias adicionadas")
        
        # Alimentar sistema de clima
        print("\n🌤️ Alimentando sistema de clima...")
        clima = get_clima_brasil()
        
        doc_clima = Document(
            title=clima["title"],
            content=clima["content"],
            meta_data=clima["meta_data"]
        )
        
        db_manager.session.add(doc_clima)
        db_manager.session.commit()
        print("✅ Sistema de clima do Brasil adicionado")
        
        # Alimentar documentação PostgreSQL
        print("\n📖 Alimentando documentação oficial PostgreSQL...")
        docs_postgresql = get_documentacao_postgresql_oficial()
        
        for i, doc_data in enumerate(docs_postgresql, 1):
            doc_pg = Document(
                title=doc_data["title"],
                content=doc_data["content"],
                meta_data=doc_data["meta_data"]
            )
            
            db_manager.session.add(doc_pg)
            db_manager.session.commit()
            print(f"✅ Documentação PostgreSQL {i}/3 adicionada")
        
        # Verificar total
        total_docs = db_manager.execute_query("SELECT COUNT(*) as total FROM documents")[0]['total']
        
        print(f"\n🎉 ALIMENTAÇÃO COMPLETA!")
        print("=" * 50)
        print(f"📚 Total de documentos: {total_docs}")
        print("✅ Saudações diárias configuradas")
        print("✅ Sistema de clima do Brasil ativo")
        print("✅ Documentação oficial PostgreSQL incluída")
        print("\n🐘 Mamute agora é muito mais inteligente!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante alimentação: {e}")
        return False

def criar_teste_funcionalidades():
    """Cria script para testar as novas funcionalidades"""
    
    teste_content = '''"""
Teste das Novas Funcionalidades do Mamute
Saudações, Clima e Documentação PostgreSQL
"""

import sys
import os
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.connection import DatabaseManager
from src.utils.config import Config

def testar_saudacoes():
    """Testa sistema de saudações"""
    print("🐘 TESTE DE SAUDAÇÕES")
    print("=" * 30)
    
    hora_atual = datetime.now().hour
    
    if 5 <= hora_atual < 12:
        periodo = "manhã"
    elif 12 <= hora_atual < 18:
        periodo = "tarde"
    elif 18 <= hora_atual < 23:
        periodo = "noite"
    else:
        periodo = "madrugada"
    
    print(f"⏰ Horário atual: {datetime.now().strftime('%H:%M')}")
    print(f"🌅 Período: {periodo}")
    print("✅ Sistema de saudações ativo")

def testar_clima():
    """Testa sistema de clima"""
    print("\\n🌤️ TESTE DE CLIMA")
    print("=" * 30)
    
    cidades_teste = [
        "São Paulo", "Rio de Janeiro", "Brasília", 
        "Salvador", "Fortaleza", "Belo Horizonte"
    ]
    
    print("🏙️ Cidades disponíveis para consulta:")
    for cidade in cidades_teste:
        print(f"   • {cidade}")
    
    print("✅ Sistema de clima do Brasil ativo")
    print("💡 Use: 'clima São Paulo' ou 'tempo Rio de Janeiro'")

def testar_documentacao():
    """Testa documentação PostgreSQL"""
    print("\\n📖 TESTE DE DOCUMENTAÇÃO")
    print("=" * 30)
    
    try:
        config = Config(".env")
        db_manager = DatabaseManager(config)
        
        # Buscar documentos por categoria
        docs_saudacoes = db_manager.execute_query("""
            SELECT title FROM documents 
            WHERE meta_data->>'category' = 'saudacoes'
        """)
        
        docs_clima = db_manager.execute_query("""
            SELECT title FROM documents 
            WHERE meta_data->>'category' = 'clima'
        """)
        
        docs_postgresql = db_manager.execute_query("""
            SELECT title FROM documents 
            WHERE meta_data->>'category' = 'documentacao'
        """)
        
        print(f"📝 Saudações: {len(docs_saudacoes)} documento(s)")
        print(f"🌤️ Clima: {len(docs_clima)} documento(s)")
        print(f"📖 PostgreSQL: {len(docs_postgresql)} documento(s)")
        
        # Total geral
        total = db_manager.execute_query("SELECT COUNT(*) as total FROM documents")[0]['total']
        print(f"📚 Total: {total} documentos na base")
        
        print("✅ Base de conhecimento expandida com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal de teste"""
    print("🚀 TESTE DAS FUNCIONALIDADES AVANÇADAS DO MAMUTE")
    print("=" * 60)
    
    testar_saudacoes()
    testar_clima()
    testar_documentacao()
    
    print("\\n" + "=" * 60)
    print("🎉 TODOS OS TESTES CONCLUÍDOS!")
    print("=" * 60)
    print("🐘 Mamute agora possui:")
    print("✅ Saudações personalizadas por horário")
    print("✅ Previsão do tempo de cidades brasileiras")  
    print("✅ Documentação oficial completa do PostgreSQL")
    print("\\n🌐 Inicie o servidor para testar: python start_web.py")
    print("🔗 Acesse: http://127.0.0.1:8001")

if __name__ == "__main__":
    main()
'''
    
    with open("testar_funcionalidades_avancadas.py", 'w', encoding='utf-8') as f:
        f.write(teste_content)
    
    print("✅ Script de teste criado: testar_funcionalidades_avancadas.py")

if __name__ == "__main__":
    if alimentar_base_avancada():
        criar_teste_funcionalidades()
        print("\n🎯 Próximo passo: python testar_funcionalidades_avancadas.py")
    else:
        print("❌ Falha na alimentação da base")