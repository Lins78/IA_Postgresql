"""
Gerenciador de chat e conversas
"""
from typing import List, Dict, Any, Optional
import json

from .agent import AIAgent
from .embeddings import EmbeddingManager
from ..database.connection import DatabaseManager
from ..utils.config import Config
from ..utils.logger import setup_logger

class ChatManager:
    """Gerenciador de conversas e contexto de chat"""
    
    def __init__(self, config: Config, db_manager: DatabaseManager, 
                 ai_agent: AIAgent, embedding_manager: EmbeddingManager):
        """
        Inicializa o gerenciador de chat
        
        Args:
            config: Configuração da aplicação
            db_manager: Gerenciador do banco de dados
            ai_agent: Agente de IA
            embedding_manager: Gerenciador de embeddings
        """
        self.config = config
        self.db_manager = db_manager
        self.ai_agent = ai_agent
        self.embedding_manager = embedding_manager
        self.logger = setup_logger(__name__, config.log_level)
        
        # Cache de contexto por sessão
        self.session_contexts = {}
    
    def start_conversation(self, user_id: Optional[str] = None) -> str:
        """
        Inicia uma nova conversa
        
        Args:
            user_id: ID do usuário (opcional)
        
        Returns:
            str: ID da sessão criada
        """
        session_id = self.ai_agent.create_session(user_id)
        self.session_contexts[session_id] = []
        
        self.logger.info(f"Nova conversa iniciada: {session_id}")
        return session_id
    
    def send_message(self, message: str, session_id: str, 
                    use_context: bool = True, search_documents: bool = True) -> Dict[str, Any]:
        """
        Envia uma mensagem e obtém resposta da IA
        
        Args:
            message: Mensagem do usuário
            session_id: ID da sessão
            use_context: Se deve usar o contexto da conversa
            search_documents: Se deve buscar em documentos relevantes
        
        Returns:
            Dict: Resposta da IA com contexto adicional
        """
        try:
            # Preparar contexto
            context = []
            
            if use_context and session_id in self.session_contexts:
                context = self.session_contexts[session_id]
            
            # Buscar documentos relevantes se solicitado
            relevant_docs = []
            if search_documents:
                relevant_docs = self.embedding_manager.search_similar_documents(
                    message, limit=3, threshold=0.7
                )
                
                if relevant_docs:
                    # Adicionar contexto dos documentos
                    doc_context = "Documentos relevantes encontrados:\\n"
                    for i, doc in enumerate(relevant_docs, 1):
                        doc_context += f"{i}. {doc['title']}\\n{doc['content']}\\n\\n"
                    
                    context.append({
                        "role": "system",
                        "content": doc_context
                    })
            
            # Obter resposta da IA
            response = self.ai_agent.chat(message, session_id, context)
            
            # Atualizar contexto da sessão
            if use_context:
                self._update_session_context(session_id, message, response["response"])
            
            # Adicionar informações dos documentos à resposta
            response["relevant_documents"] = relevant_docs
            response["context_used"] = len(context) > 0
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem: {e}")
            raise
    
    def _update_session_context(self, session_id: str, user_message: str, ai_response: str):
        """
        Atualiza o contexto da sessão
        
        Args:
            session_id: ID da sessão
            user_message: Mensagem do usuário
            ai_response: Resposta da IA
        """
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = []
        
        # Adicionar nova conversa ao contexto
        self.session_contexts[session_id].extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": ai_response}
        ])
        
        # Manter apenas as últimas 10 interações para evitar excesso de contexto
        max_context = 20  # 10 pares de pergunta/resposta
        if len(self.session_contexts[session_id]) > max_context:
            self.session_contexts[session_id] = self.session_contexts[session_id][-max_context:]
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Obtém resumo de uma conversa
        
        Args:
            session_id: ID da sessão
        
        Returns:
            Dict: Resumo da conversa
        """
        try:
            # Obter estatísticas da sessão
            session_query = """
            SELECT 
                user_id, start_time, last_activity, 
                total_messages, total_tokens, is_active
            FROM user_sessions 
            WHERE session_id = %(session_id)s
            """
            session_data = self.db_manager.execute_query(
                session_query, {"session_id": session_id}
            )
            
            if not session_data:
                return {"error": "Sessão não encontrada"}
            
            session_info = session_data[0]
            
            # Obter histórico de conversas
            history = self.ai_agent.get_conversation_history(session_id, limit=50)
            
            # Calcular estatísticas
            total_conversations = len(history)
            total_response_time = sum(conv.get('response_time', 0) for conv in history)
            avg_response_time = total_response_time / total_conversations if total_conversations > 0 else 0
            
            summary = {
                "session_id": session_id,
                "user_id": session_info.get('user_id'),
                "start_time": session_info.get('start_time'),
                "last_activity": session_info.get('last_activity'),
                "is_active": session_info.get('is_active'),
                "statistics": {
                    "total_messages": session_info.get('total_messages', 0),
                    "total_tokens": session_info.get('total_tokens', 0),
                    "total_conversations": total_conversations,
                    "average_response_time": round(avg_response_time, 2)
                },
                "recent_conversations": history[:5]  # Últimas 5 conversas
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Erro ao obter resumo da conversa: {e}")
            return {"error": str(e)}
    
    def clear_session_context(self, session_id: str):
        """
        Limpa o contexto de uma sessão
        
        Args:
            session_id: ID da sessão
        """
        if session_id in self.session_contexts:
            del self.session_contexts[session_id]
            self.logger.info(f"Contexto da sessão {session_id} limpo")
    
    def end_conversation(self, session_id: str) -> bool:
        """
        Encerra uma conversa
        
        Args:
            session_id: ID da sessão
        
        Returns:
            bool: True se encerrada com sucesso
        """
        try:
            # Marcar sessão como inativa
            query = """
            UPDATE user_sessions 
            SET is_active = false, last_activity = NOW()
            WHERE session_id = %(session_id)s
            """
            affected_rows = self.db_manager.execute_command(
                query, {"session_id": session_id}
            )
            
            # Limpar contexto local
            self.clear_session_context(session_id)
            
            success = affected_rows > 0
            if success:
                self.logger.info(f"Conversa {session_id} encerrada")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao encerrar conversa: {e}")
            return False
    
    def search_conversations(self, query: str, user_id: Optional[str] = None, 
                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca conversas por conteúdo
        
        Args:
            query: Termo de busca
            user_id: Filtrar por usuário (opcional)
            limit: Número máximo de resultados
        
        Returns:
            List[Dict]: Conversas encontradas
        """
        try:
            base_query = """
            SELECT c.session_id, c.user_message, c.ai_response, c.created_at,
                   s.user_id
            FROM conversations c
            JOIN user_sessions s ON c.session_id = s.session_id
            WHERE (c.user_message ILIKE %(query)s OR c.ai_response ILIKE %(query)s)
            """
            
            params = {"query": f"%{query}%", "limit": limit}
            
            if user_id:
                base_query += " AND s.user_id = %(user_id)s"
                params["user_id"] = user_id
            
            base_query += " ORDER BY c.created_at DESC LIMIT %(limit)s"
            
            results = self.db_manager.execute_query(base_query, params)
            
            self.logger.info(f"Busca de conversas: {len(results)} resultados para '{query}'")
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na busca de conversas: {e}")
            return []