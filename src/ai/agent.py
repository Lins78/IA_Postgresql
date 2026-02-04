"""
Agente principal de IA
"""
import openai
from typing import Dict, List, Any, Optional
import json
import time
import uuid

from ..database.connection import DatabaseManager
from ..database.models import Conversation, UserSession, AIModel
from ..utils.config import Config
from ..utils.logger import setup_logger

class AIAgent:
    """Agente de IA principal que gerencia conversas e interage com o banco"""
    
    def __init__(self, config: Config, db_manager: DatabaseManager):
        """
        Inicializa o agente de IA
        
        Args:
            config: Configuração da aplicação
            db_manager: Gerenciador do banco de dados
        """
        self.config = config
        self.db_manager = db_manager
        self.logger = setup_logger(__name__, config.log_level)
        
        # Configurar OpenAI
        openai.api_key = config.openai_api_key
        self.client = openai.OpenAI(api_key=config.openai_api_key)
        
        # Parâmetros do modelo
        self.model_name = "gpt-3.5-turbo"
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature
        
        self.logger.info("Agente de IA inicializado")
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """
        Cria uma nova sessão de usuário
        
        Args:
            user_id: ID do usuário (opcional)
        
        Returns:
            str: ID da sessão criada
        """
        session_id = str(uuid.uuid4())
        
        try:
            with self.db_manager.get_session() as session:
                user_session = UserSession(
                    session_id=session_id,
                    user_id=user_id
                )
                session.add(user_session)
                session.commit()
                
            self.logger.info(f"Nova sessão criada: {session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Erro ao criar sessão: {e}")
            raise
    
    def chat(self, message: str, session_id: str, context: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Processa uma mensagem do usuário e retorna a resposta da IA
        
        Args:
            message: Mensagem do usuário
            session_id: ID da sessão
            context: Contexto adicional da conversa
        
        Returns:
            Dict: Resposta da IA com metadados
        """
        start_time = time.time()
        
        try:
            # Verificar se OpenAI está configurada corretamente
            if (hasattr(self, 'client') and self.client is not None and 
                hasattr(self, 'api_key') and self.api_key != "your_openai_api_key_here"):
                # Usar OpenAI
                return self._chat_with_openai(message, session_id, context, start_time)
            else:
                # Usar sistema de fallback inteligente
                return self._chat_fallback(message, session_id, start_time)
                
        except Exception as e:
            self.logger.error(f"Erro no chat: {e}")
            response_time = time.time() - start_time
            
            # Retornar resposta de erro
            return {
                "response": f"Desculpe, não foi possível processar sua mensagem. Erro: {str(e)}",
                "tokens_used": 0,
                "response_time": response_time,
                "session_id": session_id,
                "error": True
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao processar chat: {e}")
            raise
    
    def _prepare_messages(self, user_message: str, context: Optional[List[Dict]] = None) -> List[Dict[str, str]]:
        """
        Prepara as mensagens para enviar ao modelo
        
        Args:
            user_message: Mensagem do usuário
            context: Contexto adicional
        
        Returns:
            List[Dict]: Mensagens formatadas
        """
        messages = [
            {
                "role": "system",
                "content": (
                    f"Você é {self.config.ai_name}, um assistente de IA especializado em análise de dados e consultas SQL. "
                    "Você tem acesso a um banco de dados PostgreSQL e pode ajudar com análises, "
                    "visualizações e insights dos dados. Sempre forneça respostas úteis e precisas. "
                    f"Seu nome é {self.config.ai_name} e você é uma IA amigável e inteligente."
                )
            }
        ]
        
        # Adicionar contexto se fornecido
        if context:
            for ctx in context[-5:]:  # Manter apenas os últimos 5 contextos
                messages.append(ctx)
        
        # Adicionar mensagem do usuário
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def _save_conversation(self, session_id: str, user_message: str, ai_response: str, 
                          tokens_used: int, response_time: float):
        """
        Salva a conversa no banco de dados
        
        Args:
            session_id: ID da sessão
            user_message: Mensagem do usuário
            ai_response: Resposta da IA
            tokens_used: Tokens utilizados
            response_time: Tempo de resposta
        """
        try:
            with self.db_manager.get_session() as session:
                conversation = Conversation(
                    session_id=session_id,
                    user_message=user_message,
                    ai_response=ai_response,
                    tokens_used=tokens_used,
                    response_time=response_time
                )
                session.add(conversation)
                session.commit()
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar conversa: {e}")
            # Não relançar a exceção para não afetar a resposta
    
    def _update_session_stats(self, session_id: str, tokens_used: int):
        """
        Atualiza estatísticas da sessão
        
        Args:
            session_id: ID da sessão
            tokens_used: Tokens utilizados
        """
        try:
            query = """
            UPDATE user_sessions 
            SET 
                last_activity = NOW(),
                total_messages = total_messages + 1,
                total_tokens = total_tokens + %(tokens)s
            WHERE session_id = %(session_id)s
            """
            self.db_manager.execute_command(
                query, 
                {"session_id": session_id, "tokens": tokens_used}
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar estatísticas da sessão: {e}")
    
    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém histórico de conversas de uma sessão
        
        Args:
            session_id: ID da sessão
            limit: Número máximo de conversas
        
        Returns:
            List[Dict]: Histórico de conversas
        """
        try:
            query = """
            SELECT user_message, ai_response, created_at, tokens_used, response_time
            FROM conversations 
            WHERE session_id = %(session_id)s
            ORDER BY created_at DESC
            LIMIT %(limit)s
            """
            result = self.db_manager.execute_query(
                query, 
                {"session_id": session_id, "limit": limit}
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico: {e}")
            return []
    
    def analyze_data(self, table_name: str, analysis_type: str = "summary") -> Dict[str, Any]:
        """
        Realiza análise de dados em uma tabela
        
        Args:
            table_name: Nome da tabela
            analysis_type: Tipo de análise (summary, statistical, etc.)
        
        Returns:
            Dict: Resultado da análise
        """
        try:
            # Verificar se a tabela existe
            tables = self.db_manager.get_all_tables()
            if table_name not in tables:
                raise ValueError(f"Tabela '{table_name}' não encontrada")
            
            # Obter informações da tabela
            table_info = self.db_manager.get_table_info(table_name)
            
            if analysis_type == "summary":
                # Análise básica da tabela
                count_query = f"SELECT COUNT(*) as total_rows FROM {table_name}"
                count_result = self.db_manager.execute_query(count_query)
                
                sample_query = f"SELECT * FROM {table_name} LIMIT 5"
                sample_result = self.db_manager.execute_query(sample_query)
                
                result = {
                    "table_name": table_name,
                    "columns": table_info,
                    "total_rows": count_result[0]['total_rows'],
                    "sample_data": sample_result
                }
                
                return result
                
        except Exception as e:
            self.logger.error(f"Erro na análise de dados: {e}")
            raise
    
    def _chat_with_openai(self, message: str, session_id: str, context: Optional[List[Dict]], start_time: float) -> Dict[str, Any]:
        """Chat usando OpenAI API"""
        # Preparar mensagens para o modelo
        messages = self._prepare_messages(message, context)
        
        # Chamar a API do OpenAI
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        # Extrair resposta
        ai_response = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        response_time = time.time() - start_time
        
        # Salvar conversa no banco
        self._save_conversation(
            session_id=session_id,
            user_message=message,
            ai_response=ai_response,
            tokens_used=tokens_used,
            response_time=response_time
        )
        
        # Atualizar estatísticas da sessão
        self._update_session_stats(session_id, tokens_used)
        
        result = {
            "response": ai_response,
            "tokens_used": tokens_used,
            "response_time": response_time,
            "session_id": session_id
        }
        
        self.logger.info(f"Resposta OpenAI para sessão {session_id}: {tokens_used} tokens, {response_time:.2f}s")
        return result
    
    def _chat_fallback(self, message: str, session_id: str, start_time: float) -> Dict[str, Any]:
        """Sistema de fallback para chat sem OpenAI"""
        from .fallback_chat import FallbackChatSystem
        
        # Inicializar sistema de fallback com acesso ao banco
        fallback_system = FallbackChatSystem(self.config, self.config.ai_name, self.db_manager)
        
        # Gerar resposta
        result = fallback_system.generate_response(message, session_id)
        
        # Salvar conversa no banco
        try:
            self._save_conversation(
                session_id=session_id,
                user_message=message,
                ai_response=result["response"],
                tokens_used=0,
                response_time=result["response_time"]
            )
            self._update_session_stats(session_id, 0)
        except Exception as e:
            self.logger.warning(f"Erro ao salvar conversa fallback: {e}")
        
        self.logger.info(f"Resposta fallback para sessão {session_id}: {result['response_time']:.2f}s")
        return result