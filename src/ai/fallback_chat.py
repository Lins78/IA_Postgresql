"""
Sistema de chat fallback para quando OpenAI não está disponível
"""
import datetime
from typing import Dict, Any
from ..utils.logger import setup_logger

class FallbackChatSystem:
    """Sistema de chat que funciona sem OpenAI"""
    
    def __init__(self, config, ai_name="Mamute", db_manager=None):
        self.config = config
        self.ai_name = ai_name
        self.db_manager = db_manager
        self.logger = setup_logger(__name__, config.log_level)
    
    def generate_response(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Gera resposta inteligente baseada em padrões
        
        Args:
            message: Mensagem do usuário
            session_id: ID da sessão
        
        Returns:
            Dict: Resposta formatada
        """
        import time
        start_time = time.time()
        
        message_lower = message.lower()
        
        # Saudações contextuais
        now = datetime.datetime.now()
        hour = now.hour
        
        if any(palavra in message_lower for palavra in ['oi', 'olá', 'hello', 'boa', 'bom', 'hey']):
            if hour < 12:
                saudacao = f"🌅 Bom dia! Sou o {self.ai_name}, sua IA especialista em PostgreSQL!"
            elif hour < 18:
                saudacao = f"🌤️ Boa tarde! Sou o {self.ai_name}, como posso ajudar com PostgreSQL hoje?"
            else:
                saudacao = f"🌙 Boa noite! Sou o {self.ai_name}, pronto para ajudar com suas consultas!"
            
            ai_response = f"{saudacao}\\n\\n📋 Posso ajudar com:\\n• Consultas SQL\\n• Otimização de banco\\n• Comandos PostgreSQL\\n• Previsão do tempo no Brasil\\n\\nComo posso ajudar?"
        
        # Previsão do tempo
        elif any(palavra in message_lower for palavra in ['tempo', 'clima', 'chuva', 'sol', 'temperatura', 'previsao']):
            ai_response = self._handle_weather_query(message_lower)
        
        # Agradecimentos
        elif any(palavra in message_lower for palavra in ['obrigado', 'obrigada', 'valeu', 'muito obrigado', 'agradeço', 'grato', 'grata']):
            ai_response = self._handle_thanks()
        
        # Despedidas
        elif any(palavra in message_lower for palavra in ['tchau', 'até logo', 'até mais', 'adeus', 'bye', 'até breve', 'falou', 'tá bom', 'ok obrigado', 'não precisa mais', 'é isso']):
            ai_response = self._handle_goodbye()
        
        # Análise e melhorias do banco
        elif any(palavra in message_lower for palavra in ['analisar', 'análise', 'melhorar', 'melhorias', 'otimizar', 'problemas', 'sugestões']):
            ai_response = self._handle_database_analysis(message_lower)
        
        # PostgreSQL help
        elif any(palavra in message_lower for palavra in ['select', 'sql', 'postgresql', 'banco', 'tabela', 'consulta']):
            # Verificar se é uma pergunta específica sobre o banco atual
            if self._is_database_query(message_lower):
                ai_response = self._handle_database_query(message_lower)
            else:
                ai_response = self._handle_sql_query(message_lower)
        
        # JOINs
        elif 'join' in message_lower:
            ai_response = self._handle_join_query()
        
        # Performance/Índices
        elif any(palavra in message_lower for palavra in ['índice', 'index', 'performance', 'otimiz', 'velocidade']):
            ai_response = self._handle_performance_query()
        
        # Funções PostgreSQL
        elif any(palavra in message_lower for palavra in ['função', 'function', 'agregad', 'count', 'sum', 'avg']):
            ai_response = self._handle_functions_query()
        
        # Agradecimentos
        elif any(palavra in message_lower for palavra in ['obrigad', 'valeu', 'muito bem', 'excelente', 'perfeito', 'ótimo trabalho']):
            ai_response = self._handle_thanks()
        
        # Despedidas
        elif any(palavra in message_lower for palavra in ['tchau', 'até logo', 'até mais', 'adeus', 'bye', 'finalizando', 'encerrar']):
            ai_response = self._handle_farewell()
        
        # Mamute info
        elif any(palavra in message_lower for palavra in ['quem', 'você', 'mamute', 'sobre']):
            ai_response = self._handle_about_query()
        
        # Agradecimentos
        elif any(palavra in message_lower for palavra in ['obrigado', 'obrigada', 'valeu', 'muito obrigado', 'agradeço', 'grato', 'grata']):
            ai_response = self._handle_thanks()
        
        # Despedidas
        elif any(palavra in message_lower for palavra in ['tchau', 'até logo', 'até mais', 'adeus', 'bye', 'até breve', 'falou', 'tá bom', 'ok obrigado', 'não precisa mais', 'é isso']):
            ai_response = self._handle_goodbye()
        
        # Resposta padrão
        else:
            ai_response = self._handle_default_query()
        
        response_time = time.time() - start_time
        
        return {
            "response": ai_response,
            "tokens_used": 0,
            "response_time": response_time,
            "session_id": session_id,
            "mode": "fallback"
        }
    
    def _handle_weather_query(self, message_lower: str) -> str:
        """Trata consultas sobre clima"""
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
            return f"🌤️ **Previsão do Tempo**\\n\\n{cidade_encontrada}\\n\\n💡 Para outras cidades, pergunte: 'Como está o tempo em [cidade]?'"
        else:
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
    
    def _handle_sql_query(self, message_lower: str) -> str:
        """Trata consultas sobre SQL"""
        return """📚 **PostgreSQL - Comandos Básicos**

🔹 **SELECT**: Consultar dados
```sql
SELECT * FROM tabela;
SELECT nome, email FROM usuarios;
SELECT * FROM produtos WHERE preco > 100;
```

🔹 **INSERT**: Inserir dados
```sql
INSERT INTO tabela (col1, col2) VALUES ('val1', 'val2');
INSERT INTO usuarios (nome, email) VALUES ('João', 'joao@email.com');
```

🔹 **UPDATE**: Atualizar dados
```sql
UPDATE tabela SET coluna = 'valor' WHERE id = 1;
UPDATE produtos SET preco = 150 WHERE id = 5;
```

🔹 **DELETE**: Remover dados
```sql
DELETE FROM tabela WHERE condição;
DELETE FROM usuarios WHERE ativo = false;
```

❓ Precisa de ajuda específica? Pergunte sobre JOINs, índices, ou otimização!"""
    
    def _handle_join_query(self) -> str:
        """Trata consultas sobre JOINs"""
        return """🔗 **PostgreSQL JOINs**

🔹 **INNER JOIN**: Registros que existem em ambas tabelas
```sql
SELECT u.nome, p.titulo
FROM usuarios u
INNER JOIN posts p ON u.id = p.usuario_id;
```

🔹 **LEFT JOIN**: Todos da tabela esquerda
```sql
SELECT u.nome, p.titulo
FROM usuarios u
LEFT JOIN posts p ON u.id = p.usuario_id;
```

🔹 **RIGHT JOIN**: Todos da tabela direita
```sql
SELECT u.nome, p.titulo
FROM usuarios u
RIGHT JOIN posts p ON u.id = p.usuario_id;
```

🔹 **FULL OUTER JOIN**: Todos de ambas as tabelas
```sql
SELECT u.nome, p.titulo
FROM usuarios u
FULL OUTER JOIN posts p ON u.id = p.usuario_id;
```

💡 **Dica**: Use INNER JOIN quando precisar apenas dos registros relacionados!"""
    
    def _handle_performance_query(self) -> str:
        """Trata consultas sobre performance"""
        return """⚡ **Otimização PostgreSQL**

🔹 **Criar Índice**:
```sql
CREATE INDEX idx_usuario_email ON usuarios(email);
CREATE INDEX idx_produto_categoria ON produtos(categoria_id);
```

🔹 **Índice Composto**:
```sql
CREATE INDEX idx_composto ON vendas(cliente_id, data_venda);
```

🔹 **Verificar Performance**:
```sql
EXPLAIN ANALYZE SELECT * FROM tabela WHERE condição;
EXPLAIN (BUFFERS, ANALYZE) SELECT * FROM grandes_tabelas;
```

🔹 **Vacuum e Analyze**:
```sql
VACUUM ANALYZE tabela;
REINDEX INDEX idx_nome;
```

📊 **Dicas**: 
• Use índices em colunas de WHERE, ORDER BY e JOIN
• Evite SELECT * em tabelas grandes
• Use LIMIT para consultas exploratórias"""
    
    def _handle_functions_query(self) -> str:
        """Trata consultas sobre funções"""
        return """🔢 **Funções PostgreSQL**

🔹 **Funções Agregadas**:
```sql
SELECT COUNT(*) FROM usuarios;
SELECT SUM(valor) FROM vendas;
SELECT AVG(preco) FROM produtos;
SELECT MAX(data_criacao) FROM posts;
SELECT MIN(idade) FROM clientes;
```

🔹 **Funções de String**:
```sql
SELECT UPPER(nome) FROM usuarios;
SELECT CONCAT(nome, ' ', sobrenome) FROM pessoas;
SELECT LENGTH(descricao) FROM produtos;
```

🔹 **Funções de Data**:
```sql
SELECT NOW(), CURRENT_DATE, CURRENT_TIME;
SELECT EXTRACT(YEAR FROM data_nascimento) FROM usuarios;
SELECT AGE(data_nascimento) FROM usuarios;
```

🔹 **GROUP BY com Agregações**:
```sql
SELECT categoria, COUNT(*), AVG(preco)
FROM produtos 
GROUP BY categoria;
```"""
    
    def _handle_about_query(self) -> str:
        """Trata consultas sobre o Mamute"""
        return f"""🐘 **Sobre o {self.ai_name}**

🤖 Sou o {self.ai_name}, sua IA especialista em PostgreSQL!

🎯 **Minha Missão**: Ajudar você com análise de dados, consultas SQL e insights inteligentes sobre seu banco PostgreSQL.

🧠 **Meus Conhecimentos**:
• 📊 Consultas SQL avançadas
• ⚡ Otimização e performance
• 🔗 Relacionamentos e JOINs
• 📈 Análise de dados
• 🌤️ Previsão do tempo brasileiro
• 💡 Melhores práticas PostgreSQL

🛠️ **Como posso ajudar**:
• Criar consultas SQL eficientes
• Explicar conceitos PostgreSQL
• Analisar performance de queries
• Sugerir otimizações
• Informar sobre clima no Brasil

❓ **Exemplos de perguntas**:
• "Como fazer um LEFT JOIN?"
• "Otimizar esta consulta"
• "Como está o tempo em São Paulo?"
• "Explicar índices PostgreSQL"

💬 Estou aqui para tornar seu trabalho com PostgreSQL mais fácil e eficiente!"""
    
    def _handle_default_query(self) -> str:
        """Resposta padrão"""
        return f"""🐘 **{self.ai_name} - IA PostgreSQL**

🤔 Não entendi completamente sua pergunta, mas posso ajudar com:

📋 **Tópicos disponíveis**:
• 🗄️ Comandos SQL (SELECT, INSERT, UPDATE, DELETE)
• 🔗 JOINs e relacionamentos
• ⚡ Otimização e índices
• 🔢 Funções e agregações
• 🌤️ Previsão do tempo brasileiro
• 📊 Análise de dados

💡 **Exemplos de perguntas**:
• "Como fazer um SELECT?"
• "Como está o tempo em São Paulo?"
• "Explicar JOINs"
• "Criar índices para performance"
• "Funções agregadas PostgreSQL"

🗣️ **Reformule sua pergunta** ou escolha um dos tópicos acima.
Como posso ajudar?"""
    
    def _is_database_query(self, message_lower: str) -> bool:
        """Verifica se é uma pergunta específica sobre o banco atual"""
        database_keywords = [
            'quantos bancos', 'quais bancos', 'listar bancos', 'nomes dos bancos',
            'quantas tabelas', 'quais tabelas', 'listar tabelas', 'nomes das tabelas',
            'tamanho da', 'tamanho do banco', 'número de registros',
            'mostrar esquema', 'estrutura da tabela', 'colunas da tabela'
        ]
        
        return any(keyword in message_lower for keyword in database_keywords)
    
    def _handle_database_query(self, message_lower: str) -> str:
        """Executa consultas específicas no banco de dados"""
        if not self.db_manager:
            return "❌ Não foi possível acessar o banco de dados. Conexão não disponível."
        
        try:
            # Consulta sobre bancos de dados
            if any(palavra in message_lower for palavra in ['quantos bancos', 'quais bancos', 'nomes dos bancos']):
                return self._query_databases()
            
            # Consulta sobre tabelas
            elif any(palavra in message_lower for palavra in ['quantas tabelas', 'quais tabelas', 'nomes das tabelas']):
                return self._query_tables()
            
            # Consulta sobre tamanho/registros
            elif any(palavra in message_lower for palavra in ['tamanho', 'registros', 'linhas']):
                return self._query_table_sizes()
            
            # Consulta sobre estrutura
            elif any(palavra in message_lower for palavra in ['estrutura', 'colunas', 'esquema']):
                return self._query_table_structure(message_lower)
            
            else:
                return self._handle_sql_query(message_lower)
                
        except Exception as e:
            return f"❌ Erro ao consultar banco de dados: {str(e)}"
    
    def _query_databases(self) -> str:
        """Lista os bancos de dados disponíveis"""
        try:
            query = "SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname;"
            result = self.db_manager.execute_query(query)
            
            if result:
                databases = [row['datname'] for row in result]
                db_list = "\n".join([f"   • {db}" for db in databases])
                
                return f"""🗄️ **Bancos de Dados PostgreSQL**

📊 **Total de bancos**: {len(databases)}

📋 **Lista de bancos**:
{db_list}

💡 **Banco atual**: {self.config.postgres_db}

🔍 **Para mais detalhes**: Pergunte sobre tabelas ou estrutura específica!"""
            else:
                return "❌ Não foi possível listar os bancos de dados."
                
        except Exception as e:
            return f"❌ Erro ao consultar bancos: {str(e)}"
    
    def _query_tables(self) -> str:
        """Lista as tabelas do banco atual"""
        try:
            query = """SELECT table_name, table_type 
                       FROM information_schema.tables 
                       WHERE table_schema = 'public' 
                       ORDER BY table_name;"""
            result = self.db_manager.execute_query(query)
            
            if result:
                tables = []
                for row in result:
                    icon = "📋" if row['table_type'] == 'BASE TABLE' else "👁️"
                    tables.append(f"   {icon} {row['table_name']}")
                
                table_list = "\n".join(tables)
                
                return f"""📋 **Tabelas do Banco '{self.config.postgres_db}'**

📊 **Total de tabelas**: {len(result)}

🗂️ **Lista de tabelas**:
{table_list}

🔍 **Para mais detalhes**: Pergunte sobre uma tabela específica!
💡 **Exemplo**: "Estrutura da tabela usuarios" ou "Quantos registros tem a tabela produtos"""
            else:
                return "❌ Nenhuma tabela encontrada no banco atual."
                
        except Exception as e:
            return f"❌ Erro ao consultar tabelas: {str(e)}"
    
    def _query_table_sizes(self) -> str:
        """Mostra o tamanho das tabelas"""
        try:
            query = """SELECT 
                         schemaname,
                         tablename,
                         pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
                       FROM pg_tables 
                       WHERE schemaname = 'public' 
                       ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"""
            result = self.db_manager.execute_query(query)
            
            if result:
                table_sizes = []
                for row in result:
                    table_sizes.append(f"   📊 {row['tablename']}: {row['size']}")
                
                sizes_list = "\n".join(table_sizes)
                
                return f"""📊 **Tamanho das Tabelas**

💾 **Banco**: {self.config.postgres_db}

📈 **Tamanhos por tabela**:
{sizes_list}

💡 **Para contagem de registros**: Pergunte "Quantos registros tem a tabela [nome]"""
            else:
                return "❌ Não foi possível obter informações de tamanho."
                
        except Exception as e:
            return f"❌ Erro ao consultar tamanhos: {str(e)}"
    
    def _query_table_structure(self, message_lower: str) -> str:
        """Mostra a estrutura de uma tabela específica"""
        # Tentar extrair nome da tabela da mensagem
        words = message_lower.split()
        table_name = None
        
        # Procurar por palavras que podem ser nome de tabela
        for i, word in enumerate(words):
            if word in ['tabela', 'table'] and i + 1 < len(words):
                table_name = words[i + 1]
                break
        
        if not table_name:
            return """🔍 **Estrutura de Tabela**

❓ Especifique o nome da tabela!

💡 **Exemplo**: "Estrutura da tabela usuarios" ou "Colunas da tabela produtos"

📋 **Para ver todas as tabelas**: Pergunte "Quais tabelas existem?"""
        
        try:
            query = """SELECT 
                         column_name,
                         data_type,
                         is_nullable,
                         column_default
                       FROM information_schema.columns 
                       WHERE table_name = %s AND table_schema = 'public'
                       ORDER BY ordinal_position;"""
            result = self.db_manager.execute_query(query, (table_name,))
            
            if result:
                columns = []
                for row in result:
                    nullable = "NULL" if row['is_nullable'] == 'YES' else "NOT NULL"
                    default = f" DEFAULT {row['column_default']}" if row['column_default'] else ""
                    columns.append(f"   📝 {row['column_name']}: {row['data_type']} {nullable}{default}")
                
                columns_list = "\n".join(columns)
                
                return f"""🏗️ **Estrutura da Tabela '{table_name}'**

📊 **Colunas** ({len(result)} total):
{columns_list}

💡 **Para dados**: Pergunte "Mostrar dados da tabela {table_name}"""
            else:
                return f"❌ Tabela '{table_name}' não encontrada ou sem colunas."
                
        except Exception as e:
            return f"❌ Erro ao consultar estrutura: {str(e)}"
    
    def _handle_database_analysis(self, message_lower: str) -> str:
        """Realiza análise completa do banco de dados"""
        if not self.db_manager:
            return "❌ Não foi possível acessar o banco de dados para análise."
        
        try:
            # Análise completa do banco
            analysis_results = self._perform_comprehensive_analysis()
            return self._format_analysis_report(analysis_results)
            
        except Exception as e:
            return f"❌ Erro durante análise: {str(e)}"
    
    def _perform_comprehensive_analysis(self) -> dict:
        """Executa análise completa do banco de dados"""
        results = {
            'database_info': self._analyze_database_info(),
            'tables_analysis': self._analyze_tables_structure(),
            'indexes_analysis': self._analyze_indexes(),
            'performance_issues': self._identify_performance_issues(),
            'security_issues': self._check_security_issues(),
            'optimization_suggestions': self._generate_optimization_suggestions()
        }
        return results
    
    def _analyze_database_info(self) -> dict:
        """Analisa informações gerais do banco"""
        try:
            # Informações básicas do banco
            db_size_query = """
                SELECT pg_size_pretty(pg_database_size(current_database())) as database_size,
                       current_database() as database_name,
                       version() as postgres_version
            """
            
            # Número de conexões
            connections_query = """
                SELECT count(*) as active_connections 
                FROM pg_stat_activity 
                WHERE state = 'active'
            """
            
            db_info = self.db_manager.execute_query(db_size_query)[0]
            conn_info = self.db_manager.execute_query(connections_query)[0]
            
            return {
                'name': db_info['database_name'],
                'size': db_info['database_size'],
                'version': db_info['postgres_version'][:50],
                'active_connections': conn_info['active_connections']
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_tables_structure(self) -> list:
        """Analisa estrutura das tabelas"""
        try:
            # Tabelas com informações detalhadas
            tables_query = """
                SELECT 
                    t.table_name,
                    t.table_type,
                    pg_size_pretty(pg_total_relation_size(c.oid)) as size,
                    pg_stat_get_tuples_inserted(c.oid) as inserts,
                    pg_stat_get_tuples_updated(c.oid) as updates,
                    pg_stat_get_tuples_deleted(c.oid) as deletes
                FROM information_schema.tables t
                JOIN pg_class c ON c.relname = t.table_name
                WHERE t.table_schema = 'public' 
                  AND t.table_type = 'BASE TABLE'
                ORDER BY pg_total_relation_size(c.oid) DESC
            """
            
            tables = self.db_manager.execute_query(tables_query)
            
            # Análise de cada tabela
            detailed_analysis = []
            for table in tables:
                table_analysis = self._analyze_individual_table(table['table_name'])
                table_analysis.update(table)
                detailed_analysis.append(table_analysis)
            
            return detailed_analysis
            
        except Exception as e:
            return [{'error': str(e)}]
    
    def _analyze_individual_table(self, table_name: str) -> dict:
        """Analisa tabela individual"""
        try:
            # Contagem de registros
            count_query = f"SELECT COUNT(*) as row_count FROM {table_name}"
            count_result = self.db_manager.execute_query(count_query)
            
            # Colunas sem índices
            columns_query = """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = %s AND table_schema = 'public'
                ORDER BY ordinal_position
            """
            columns = self.db_manager.execute_query(columns_query, (table_name,))
            
            # Verificar chaves primárias
            pk_query = """
                SELECT a.attname
                FROM pg_index i
                JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                WHERE i.indrelid = %s::regclass AND i.indisprimary
            """
            
            try:
                primary_keys = self.db_manager.execute_query(pk_query, (table_name,))
                has_primary_key = len(primary_keys) > 0
            except:
                has_primary_key = False
            
            return {
                'row_count': count_result[0]['row_count'] if count_result else 0,
                'column_count': len(columns),
                'has_primary_key': has_primary_key,
                'nullable_columns': sum(1 for col in columns if col['is_nullable'] == 'YES'),
                'issues': self._identify_table_issues(table_name, columns, has_primary_key)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_indexes(self) -> list:
        """Analisa índices do banco"""
        try:
            indexes_query = """
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """
            
            indexes = self.db_manager.execute_query(indexes_query)
            
            # Análise dos índices
            index_analysis = {
                'total_indexes': len(indexes),
                'tables_without_indexes': self._find_tables_without_indexes(),
                'duplicate_indexes': self._find_duplicate_indexes(),
                'unused_indexes': []
            }
            
            return index_analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def _identify_performance_issues(self) -> list:
        """Identifica problemas de performance"""
        issues = []
        
        try:
            # Tabelas grandes sem índices
            large_tables_query = """
                SELECT t.table_name, pg_size_pretty(pg_total_relation_size(c.oid)) as size
                FROM information_schema.tables t
                JOIN pg_class c ON c.relname = t.table_name
                WHERE t.table_schema = 'public' 
                  AND pg_total_relation_size(c.oid) > 1048576
                ORDER BY pg_total_relation_size(c.oid) DESC
            """
            
            large_tables = self.db_manager.execute_query(large_tables_query)
            
            for table in large_tables:
                # Verificar se tem índices além da PK
                index_count_query = """
                    SELECT COUNT(*) as index_count 
                    FROM pg_indexes 
                    WHERE tablename = %s AND schemaname = 'public'
                """
                
                index_count = self.db_manager.execute_query(index_count_query, (table['table_name'],))
                
                if index_count and index_count[0]['index_count'] <= 1:
                    issues.append({
                        'type': 'performance',
                        'severity': 'high',
                        'table': table['table_name'],
                        'issue': f"Tabela grande ({table['size']}) com poucos índices",
                        'suggestion': f"Considere adicionar índices nas colunas mais consultadas da tabela {table['table_name']}"
                    })
            
        except Exception as e:
            issues.append({'error': str(e)})
        
        return issues
    
    def _check_security_issues(self) -> list:
        """Verifica problemas de segurança"""
        issues = []
        
        try:
            # Verificar tabelas sem chave primária
            no_pk_query = """
                SELECT table_name
                FROM information_schema.tables t
                WHERE t.table_schema = 'public' 
                  AND t.table_type = 'BASE TABLE'
                  AND NOT EXISTS (
                    SELECT 1 FROM information_schema.table_constraints tc
                    WHERE tc.table_name = t.table_name 
                      AND tc.constraint_type = 'PRIMARY KEY'
                  )
            """
            
            tables_no_pk = self.db_manager.execute_query(no_pk_query)
            
            for table in tables_no_pk:
                issues.append({
                    'type': 'security',
                    'severity': 'medium',
                    'table': table['table_name'],
                    'issue': 'Tabela sem chave primária',
                    'suggestion': f"Adicione uma chave primária na tabela {table['table_name']}"
                })
                
        except Exception as e:
            issues.append({'error': str(e)})
        
        return issues
    
    def _generate_optimization_suggestions(self) -> list:
        """Gera sugestões de otimização específicas"""
        suggestions = []
        
        try:
            # Analisar uso de VACUUM
            suggestions.append({
                'category': 'maintenance',
                'priority': 'high',
                'title': 'Manutenção Regular',
                'description': 'Execute VACUUM ANALYZE regularmente',
                'command': 'VACUUM ANALYZE;'
            })
            
            # Sugerir backup strategy
            suggestions.append({
                'category': 'backup',
                'priority': 'critical',
                'title': 'Estratégia de Backup',
                'description': 'Implemente backups automáticos regulares',
                'command': 'pg_dump ia_database > backup_$(date +%Y%m%d).sql'
            })
            
            # Monitoramento
            suggestions.append({
                'category': 'monitoring',
                'priority': 'medium',
                'title': 'Monitoramento de Performance',
                'description': 'Configure monitoramento de consultas lentas',
                'command': 'SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;'
            })
            
        except Exception as e:
            suggestions.append({'error': str(e)})
        
        return suggestions
    
    def _identify_table_issues(self, table_name: str, columns: list, has_primary_key: bool) -> list:
        """Identifica problemas específicos da tabela"""
        issues = []
        
        if not has_primary_key:
            issues.append("Sem chave primária")
        
        # Muitas colunas nullable
        nullable_count = sum(1 for col in columns if col['is_nullable'] == 'YES')
        if nullable_count > len(columns) * 0.7:
            issues.append("Muitas colunas permitem NULL")
        
        return issues
    
    def _find_tables_without_indexes(self) -> list:
        """Encontra tabelas sem índices"""
        try:
            query = """
                SELECT t.table_name
                FROM information_schema.tables t
                WHERE t.table_schema = 'public' 
                  AND t.table_type = 'BASE TABLE'
                  AND NOT EXISTS (
                    SELECT 1 FROM pg_indexes i
                    WHERE i.tablename = t.table_name AND i.schemaname = 'public'
                  )
            """
            result = self.db_manager.execute_query(query)
            return [row['table_name'] for row in result]
        except:
            return []
    
    def _find_duplicate_indexes(self) -> list:
        """Encontra índices duplicados"""
        # Implementação simplificada
        return []
    
    def _format_analysis_report(self, results: dict) -> str:
        """Formata o relatório de análise em formato de lista organizada"""
        db_info = results.get('database_info', {})
        tables = results.get('tables_analysis', [])
        performance_issues = results.get('performance_issues', [])
        security_issues = results.get('security_issues', [])
        suggestions = results.get('optimization_suggestions', [])
        
        report = f"""🔍 **ANÁLISE COMPLETA DO BANCO DE DADOS**

📊 **INFORMAÇÕES GERAIS:**
├─ 🏷️ Nome do Banco: {db_info.get('name', 'N/A')}
├─ 💾 Tamanho Total: {db_info.get('size', 'N/A')}
├─ 🔗 Conexões Ativas: {db_info.get('active_connections', 0)}
└─ 📋 Total de Tabelas: {len([t for t in tables if 'error' not in t])}

"""
        
        # Análise das tabelas
        if tables and 'error' not in tables[0]:
            report += "🗄️ **ANÁLISE DAS TABELAS:**\n"
            for i, table in enumerate(tables[:5], 1):  # Primeiras 5 tabelas
                if 'error' not in table:
                    report += f"├─ {i}. 📊 **{table['table_name']}**\n"
                    report += f"│   ├─ Registros: {table.get('row_count', 0):,}\n"
                    report += f"│   ├─ Tamanho: {table['size']}\n"
                    report += f"│   ├─ Colunas: {table.get('column_count', 0)}\n"
                    if table.get('issues'):
                        report += f"│   └─ ⚠️ Problemas: {', '.join(table['issues'])}\n"
                    else:
                        report += f"│   └─ ✅ Status: OK\n"
            report += "\n"
        
        # Problemas de performance
        if performance_issues:
            report += "⚡ **PROBLEMAS DE PERFORMANCE:**\n"
            for i, issue in enumerate(performance_issues[:3], 1):
                if 'error' not in issue:
                    severity_icon = "🔴" if issue.get('severity') == 'high' else "🟡"
                    report += f"├─ {i}. {severity_icon} **{issue.get('table', 'Sistema')}**\n"
                    report += f"│   ├─ Problema: {issue.get('issue', 'Não especificado')}\n"
                    report += f"│   └─ 💡 Solução: {issue.get('suggestion', 'Consulte um DBA')}\n"
            report += "\n"
        
        # Problemas de segurança
        if security_issues:
            report += "🔒 **PROBLEMAS DE SEGURANÇA:**\n"
            for i, issue in enumerate(security_issues[:3], 1):
                if 'error' not in issue:
                    report += f"├─ {i}. 🛡️ **{issue.get('table', 'Sistema')}**\n"
                    report += f"│   ├─ Problema: {issue.get('issue', 'Não especificado')}\n"
                    report += f"│   └─ 🔧 Correção: {issue.get('suggestion', 'Consulte documentação')}\n"
            report += "\n"
        
        # Sugestões de otimização
        if suggestions:
            report += "🚀 **SUGESTÕES DE MELHORIAS:**\n"
            for i, suggestion in enumerate(suggestions[:4], 1):
                if 'error' not in suggestion:
                    priority_icon = "🔴" if suggestion.get('priority') == 'critical' else "🟡" if suggestion.get('priority') == 'high' else "🟢"
                    report += f"├─ {i}. {priority_icon} **{suggestion.get('title', 'Melhoria')}**\n"
                    report += f"│   ├─ Descrição: {suggestion.get('description', 'Sem descrição')}\n"
                    if suggestion.get('command'):
                        report += f"│   └─ 💻 Comando: `{suggestion['command']}`\n"
                    else:
                        report += f"│   └─ 📋 Ação necessária\n"
            report += "\n"
        
        report += """📋 **PRÓXIMOS PASSOS RECOMENDADOS:**
├─ 1. 🔧 Corrija problemas de segurança (chaves primárias)
├─ 2. ⚡ Implemente índices nas tabelas grandes  
├─ 3. 🔄 Configure rotina de VACUUM ANALYZE
├─ 4. 💾 Estabeleça estratégia de backup
└─ 5. 📊 Configure monitoramento de performance

❓ **Quer detalhes específicos?** 
Pergunte sobre qualquer tabela ou problema identificado!"""
        
        return report
    
    def _handle_thanks(self) -> str:
        """Trata agradecimentos do usuário"""
        import datetime
        
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M")
        
        responses = [
            f"😊 Fico feliz em ter ajudado! ({time_str})\n\n🤗 É sempre um prazer trabalhar com PostgreSQL!\n\n❓ **Posso ajudar em mais alguma coisa?**\n• Análise de outras tabelas\n• Otimizações específicas\n• Consultas SQL\n• Dúvidas sobre PostgreSQL",
            f"🐘 De nada! Foi ótimo analisar seu banco! ({time_str})\n\n✨ Adoro resolver problemas de banco de dados!\n\n🔍 **Há mais algo que posso fazer?**\n• Consultas específicas\n• Relatórios detalhados\n• Sugestões de melhorias\n• Previsão do tempo 😄",
            f"🎯 Que bom que foi útil! ({time_str})\n\n💪 Estou sempre pronto para PostgreSQL!\n\n🚀 **Mais alguma tarefa?**\n• Análises adicionais\n• Comandos SQL\n• Dicas de otimização\n• Qualquer dúvida!"
        ]
        
        import random
        return random.choice(responses)
    
    def _handle_farewell(self) -> str:
        """Trata despedidas do usuário"""
        import datetime
        
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M")
        date_str = now.strftime("%d/%m/%Y")
        hour = now.hour
        
        # Mensagem baseada no horário
        if hour < 12:
            period_msg = "Tenha um ótimo dia!"
            icon = "🌅"
        elif hour < 18:
            period_msg = "Boa tarde e até logo!"
            icon = "🌤️"
        else:
            period_msg = "Boa noite e até amanhã!"
            icon = "🌙"
        
        return f"""{icon} **Até logo!** ({time_str} - {date_str})

🐘 **Foi um prazer ajudar com seu PostgreSQL!**

📋 **Resumo da nossa conversa:**
• Análise completa do banco de dados
• Identificação de melhorias
• Sugestões de otimização
• Comandos SQL específicos

🎯 **Lembre-se das principais recomendações:**
├─ Implementar índices nas tabelas grandes
├─ Configurar rotina de backup
├─ Executar VACUUM ANALYZE regularmente
└─ Monitorar performance

💡 **Sempre que precisar do Mamute:**
• Análises de banco de dados
• Consultas PostgreSQL
• Otimizações de performance
• Previsão do tempo brasileiro 🌤️

{period_msg} 🚀

🔗 **Acesse novamente:** http://127.0.0.1:8001/chat"""
    
    def _handle_default_query(self) -> str:
        """Resposta padrão"""
        return f"""🐘 **{self.ai_name} - IA PostgreSQL**

🤔 Não entendi completamente sua pergunta, mas posso ajudar com:

📋 **Tópicos disponíveis**:
• 🗄️ Comandos SQL (SELECT, INSERT, UPDATE, DELETE)
• 🔗 JOINs e relacionamentos
• ⚡ Otimização e índices
• 🔢 Funções e agregações
• 🌤️ Previsão do tempo brasileiro
• 📊 Análise de dados

💡 **Exemplos de perguntas**:
• "Como fazer um SELECT?"
• "Como está o tempo em São Paulo?"
• "Explicar JOINs"
• "Criar índices para performance"
• "Funções agregadas PostgreSQL"

🗣️ **Reformule sua pergunta** ou escolha um dos tópicos acima.
Como posso ajudar?"""