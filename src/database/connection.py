"""
Gerenciador de conexão com PostgreSQL
"""
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from typing import Dict, List, Any, Optional
import logging

from ..utils.config import Config
from ..utils.logger import setup_logger

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
        
        # Configuração do SQLAlchemy
        self.engine = create_engine(
            config.database_url,
            echo=config.debug,
            pool_size=10,
            max_overflow=20
        )
        
        self.Session = sessionmaker(bind=self.engine)
        self.logger.info("Gerenciador de banco de dados inicializado")
    
    def test_connection(self) -> bool:
        """
        Testa a conexão com o banco de dados
        
        Returns:
            bool: True se a conexão for bem-sucedida
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                self.logger.info("Conexão com PostgreSQL estabelecida com sucesso")
                return True
        except Exception as e:
            self.logger.error(f"Erro ao conectar com PostgreSQL: {e}")
            return False
    
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
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Executa uma query SELECT e retorna os resultados
        
        Args:
            query: Query SQL
            params: Parâmetros da query
        
        Returns:
            List[Dict]: Lista com os resultados
        """
        try:
            with psycopg2.connect(self.config.database_url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, params or {})
                    results = [dict(row) for row in cursor.fetchall()]
                    self.logger.debug(f"Query executada: {len(results)} resultados")
                    return results
        except Exception as e:
            self.logger.error(f"Erro ao executar query: {e}")
            raise
    
    def execute_command(self, command: str, params: Optional[Dict] = None) -> int:
        """
        Executa um comando SQL (INSERT, UPDATE, DELETE)
        
        Args:
            command: Comando SQL
            params: Parâmetros do comando
        
        Returns:
            int: Número de linhas afetadas
        """
        try:
            with psycopg2.connect(self.config.database_url) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(command, params or {})
                    conn.commit()
                    affected_rows = cursor.rowcount
                    self.logger.debug(f"Comando executado: {affected_rows} linhas afetadas")
                    return affected_rows
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