"""
Gerenciador de conexão com PostgreSQL
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
from typing import Dict, List, Any, Optional
import logging
import re

from ..utils.config import Config
from ..utils.logger import setup_logger
import os

# Base para modelos SQLAlchemy
Base = declarative_base()

class DatabaseManager:
    """Gerenciador de conexão e operações com PostgreSQL"""
    
    def __init__(self, config: Config):
        """
        Inicializa o gerenciador de banco de dados
        
        Args:
            config: Instância da configuração
        """
        self.config = config
        self.logger = setup_logger(__name__, config.log_level)
        self.current_database = None

        # Validação de identificadores SQL simples
        self._identifier_pattern = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        
        # Configuração do SQLAlchemy
        self.engine = create_engine(
            config.database_url,
            echo=config.debug,
            pool_size=10,
            max_overflow=20
        )
        
        self.Session = sessionmaker(bind=self.engine)
        self.logger.info("Gerenciador de banco de dados inicializado")
        
        # Descobrir banco atual
        try:
            result = self.execute_query("SELECT current_database()")
            if result:
                self.current_database = result[0]['current_database']
        except:
            pass
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com o banco de dados
        
        Returns:
            bool: True se a conexão for bem-sucedida
        """
        try:
            with self.engine.connect() as connection:
                from sqlalchemy import text
                result = connection.execute(text("SELECT 1"))
                self.logger.info("Conexão com PostgreSQL estabelecida com sucesso")
                return True
        except Exception as e:
            self.logger.error(f"Erro ao conectar com PostgreSQL: {e}")
            return False

    # ---------- Identificadores seguros ----------
    def assert_valid_identifier(self, name: str):
        """Valida identificadores simples de tabela/schema/coluna."""
        if not name or len(name) > 128 or not self._identifier_pattern.match(name):
            raise ValueError("Identificador inválido: use apenas letras, números e sublinhado, iniciando por letra ou _ e até 128 caracteres.")
        return True

    # ---------- Segurança SQL ----------
    @staticmethod
    def is_safe_select(query: str) -> bool:
        """Valida se a query é um SELECT seguro (sem DDL/DML perigosos)."""
        if not query:
            return False

        # Remover espaços e ponto e vírgula final
        query_clean = query.strip().rstrip(";")
        upper = query_clean.upper()

        # Permitir WITH ou SELECT apenas no início
        starts_with_select = upper.startswith("SELECT")
        starts_with_with = upper.startswith("WITH")
        if not (starts_with_select or starts_with_with):
            return False

        # Bloquear palavras perigosas comuns em DDL/DML/controle
        forbidden = [
            r"\\bINSERT\\b", r"\\bUPDATE\\b", r"\\bDELETE\\b", r"\\bDROP\\b",
            r"\\bALTER\\b", r"\\bCREATE\\b", r"\\bTRUNCATE\\b", r"\\bGRANT\\b",
            r"\\bREVOKE\\b", r"\\bCOPY\\b", r"\\bDO\\b", r"\\bBEGIN\\b",
            r"\\bCOMMIT\\b", r"\\bROLLBACK\\b"
        ]

        for pattern in forbidden:
            if re.search(pattern, upper, flags=re.IGNORECASE):
                return False

        # Evitar múltiplas instruções
        if ";" in query_clean:
            return False

        return True

    @staticmethod
    def assert_safe_select(query: str):
        """Lança exceção se a query não for um SELECT seguro."""
        if not DatabaseManager.is_safe_select(query):
            raise ValueError("Apenas consultas SELECT simples são permitidas para este endpoint.")
    
    @contextmanager
    def get_session(self):
        """
        Context manager para sessões do SQLAlchemy
        
        Yields:
            Session: Sessão do SQLAlchemy
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Erro na sessão do banco: {e}")
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str, params: Optional[Any] = None, actor: Optional[str] = None) -> List[Dict[str, Any]]:
        """Executa SELECT reutilizando pool do SQLAlchemy (raw psycopg2).

        Adiciona logging/auditoria simples com o identificador opcional `actor`.
        """
        try:
            # Audit log (informational)
            log_actor = actor or 'app'
            self.logger.info(f"[DB AUDIT] actor={log_actor} query={query[:200]}")

            # Se o actor for 'ai' e existir credenciais específicas, use engine temporário
            use_temp_engine = False
            temp_engine = None
            if actor and actor.lower().startswith('ai'):
                ai_user = os.getenv('AI_DB_USER')
                ai_pass = os.getenv('AI_DB_PASSWORD')
                if ai_user and ai_pass:
                    try:
                        parsed = make_url(self.config.database_url)
                        new_url = parsed.set(username=ai_user, password=ai_pass)
                        temp_engine = create_engine(new_url, echo=self.config.debug, pool_size=5, max_overflow=5)
                        use_temp_engine = True
                    except Exception as e:
                        self.logger.warning(f"Não foi possível criar engine temporária para actor ai: {e}")

            conn = (temp_engine or self.engine).raw_connection()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, params or ())
                    rows = [dict(row) for row in cursor.fetchall()]
                    self.logger.debug(f"Query executada: {len(rows)} resultados")
                    return rows
            finally:
                conn.close()
        except Exception as e:
            self.logger.error(f"Erro ao executar query: {e}")
            raise
    
    def execute_command(self, command: str, params: Optional[Any] = None, actor: Optional[str] = None) -> int:
        """Executa INSERT/UPDATE/DELETE reutilizando pool do SQLAlchemy (raw psycopg2).

        Adiciona logging/auditoria simples com o identificador opcional `actor`.
        """
        try:
            log_actor = actor or 'app'
            self.logger.info(f"[DB AUDIT] actor={log_actor} command={command[:200]}")

            # Suporta execução com credenciais AI quando actor indica
            temp_engine = None
            if actor and actor.lower().startswith('ai'):
                ai_user = os.getenv('AI_DB_USER')
                ai_pass = os.getenv('AI_DB_PASSWORD')
                if ai_user and ai_pass:
                    try:
                        parsed = make_url(self.config.database_url)
                        new_url = parsed.set(username=ai_user, password=ai_pass)
                        temp_engine = create_engine(new_url, echo=self.config.debug, pool_size=5, max_overflow=5)
                    except Exception as e:
                        self.logger.warning(f"Não foi possível criar engine temporária para actor ai: {e}")

            conn = (temp_engine or self.engine).raw_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute(command, params or ())
                    affected_rows = cursor.rowcount or 0
                    conn.commit()
                    self.logger.debug(f"Comando executado: {affected_rows} linhas afetadas")
                    return affected_rows
            finally:
                conn.close()
        except Exception as e:
            self.logger.error(f"Erro ao executar comando: {e}")
            raise
    
    def create_tables(self):
        """Cria todas as tabelas definidas nos modelos"""
        try:
            Base.metadata.create_all(self.engine)
            self.logger.info("Tabelas criadas com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao criar tabelas: {e}")
            raise

    def ensure_schema_columns(self):
        """Adiciona colunas ausentes necessárias para a aplicação quando as tabelas existem."""
        try:
            self.execute_command(
                "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();"
            )
            self.execute_command(
                "ALTER TABLE queries ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();"
            )
            self.logger.info("Colunas de esquema ausentes garantidas com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao garantir colunas de esquema: {e}")
            raise

    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Obtém informações sobre uma tabela
        
        Args:
            table_name: Nome da tabela
        
        Returns:
            List[Dict]: Informações das colunas
        """
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = %(table_name)s
        ORDER BY ordinal_position
        """
        return self.execute_query(query, {"table_name": table_name})
    
    def get_all_tables(self) -> List[str]:
        """
        Obtém lista de todas as tabelas do banco
        
        Returns:
            List[str]: Lista com nomes das tabelas
        """
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
        """
        result = self.execute_query(query)
        return [row['table_name'] for row in result]

    def get_schemas(self) -> List[str]:
        """
        Obtém lista de schemas disponíveis no banco de dados.
        """
        query = """
        SELECT schema_name
        FROM information_schema.schemata
        ORDER BY schema_name
        """
        result = self.execute_query(query)
        return [row['schema_name'] for row in result]
    
    def switch_database(self, database_name: str) -> bool:
        """
        Muda para um banco de dados específico
        
        Args:
            database_name: Nome do banco de dados
            
        Returns:
            bool: True se conseguiu mudar, False caso contrário
        """
        try:
            self.assert_valid_identifier(database_name)

            # Criar nova URL de conexão com o banco específico de forma segura
            parsed_url = make_url(self.config.database_url)
            new_url = parsed_url.set(database=database_name)
            
            new_engine = create_engine(
                new_url,
                echo=self.config.debug,
                pool_size=10,
                max_overflow=20
            )
            
            # Testar conexão
            with new_engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("SELECT 1"))
            
            # Se chegou aqui, conexão é válida
            self.engine = new_engine
            self.Session = sessionmaker(bind=self.engine)
            self.current_database = database_name
            self.config.database_url = str(new_url)
            
            self.logger.info(f"Mudou para banco de dados: {database_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao mudar para banco {database_name}: {e}")
            return False
    
    def get_available_databases(self) -> List[str]:
        """
        Lista todos os bancos de dados disponíveis
        
        Returns:
            List[str]: Lista com nomes dos bancos
        """
        query = """
        SELECT datname 
        FROM pg_database 
        WHERE datistemplate = false 
        ORDER BY datname
        """
        try:
            result = self.execute_query(query)
            return [row['datname'] for row in result]
        except Exception as e:
            self.logger.error(f"Erro ao listar bancos: {e}")
            return []