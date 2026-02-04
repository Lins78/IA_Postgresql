"""
Modelos de dados para o PostgreSQL
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.sql import func
from datetime import datetime

from .connection import Base

class Conversation(Base):
    """Modelo para armazenar conversas com a IA"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    tokens_used = Column(Integer, default=0)
    response_time = Column(Float, default=0.0)  # em segundos
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, session_id='{self.session_id}')>"

class Document(Base):
    """Modelo para armazenar documentos e embeddings"""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    file_path = Column(String(1000))
    file_type = Column(String(50))
    embedding = Column(JSON)  # Vetor de embedding
    meta_data = Column(JSON)  # Metadados adicionais
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}')>"

class Query(Base):
    """Modelo para armazenar queries realizadas no banco"""
    __tablename__ = 'queries'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    query_type = Column(String(50))  # SELECT, INSERT, UPDATE, DELETE
    execution_time = Column(Float, default=0.0)  # em segundos
    rows_affected = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Query(id={self.id}, type='{self.query_type}')>"

class AIModel(Base):
    """Modelo para configurações e estatísticas de modelos de IA"""
    __tablename__ = 'ai_models'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    provider = Column(String(50), nullable=False)  # OpenAI, Anthropic, etc.
    version = Column(String(50))
    max_tokens = Column(Integer)
    temperature = Column(Float)
    total_requests = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<AIModel(id={self.id}, name='{self.name}')>"

class UserSession(Base):
    """Modelo para sessões de usuários"""
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(String(255))  # Identificador do usuário (opcional)
    start_time = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())
    total_messages = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    meta_data = Column(JSON)  # Dados adicionais da sessão
    
    def __repr__(self):
        return f"<UserSession(session_id='{self.session_id}')>"