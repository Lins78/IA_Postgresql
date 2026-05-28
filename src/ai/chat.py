"""
Gerenciador de chat e conversas

Este módulo implementa o ChatManager, responsável por:
 - Gerenciar sessões deative rsa com IA
 - Integrar com banco PostgreSQL
 - Buscar documentos relevantes via embeddings
 - Garantir segurança e performance

Exemplo de uso:
    from ai.chat import ChatManager
    chat = ChatManager(config, db_manager, ai_agent, embedding_manager)
    session_id = chat.start_conversation(user_id="123")
    resposta = chat.send_message("Olá IA!", session_id)
    print(resposta["response"])
"""
from typing import List, Dict, Any, Optional
from typing import Dict, Any, List
import time

try:
    from .agent import AIAgent
    from .embeddings import EmbeddingManager
    from ..database.connection import DatabaseManager
    from ..utils.config import Config
    from ..utils.logger import setup_logger
except ImportError:
    # Permite execução direta do script
    from ai.agent import AIAgent
    from ai.embeddings import EmbeddingManager
    from database.connection import DatabaseManager
    from utils.config import Config
    from utils.logger import setup_logger

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
        # Monitoramento
        self.metrics: Dict[str, Any] = {
            'messages': 0,
            'errors': 0,
            'response_times': []
        }
        self.config = config
        self.db_manager = db_manager
        self.ai_agent = ai_agent
        self.embedding_manager = embedding_manager
        self.logger = setup_logger(__name__, config.log_level)
        self.sensitive_fields = ['openai_api_key', 'database_url', 'password']
        # Cache de contexto por sessão
        self.session_contexts: Dict[str, List[Dict[str, Any]]] = {}
        self.session_context_last_used: Dict[str, float] = {}
        self.max_context_sessions = 200
        self.context_ttl_seconds = 60 * 60  # 1h
        self.doc_cache: Dict[str, Dict[str, Any]] = {}
        self.doc_cache_ttl = 300  # segundos
    
    def start_conversation(self, user_id: Optional[str] = None) -> str:
        """
        Inicia uma nova conversa
        
        Args:
            user_id: ID do usuário (opcional)
        
        Returns:
            str: ID da sessão criada
        """
        # Verificar disponibilidade do PostgreSQL antes de criar sessão
        if not self.db_manager.test_connection():
            raise RuntimeError("Não foi possível localizar uma instância PostgreSQL ativa. Ajuste o DATABASE_URL ou suba o servidor.")

        session_id = self.ai_agent.create_session(user_id)
        self.session_contexts: Dict[str, List[Dict[str, Any]]] = {}
        self.session_contexts[session_id] = []
        self._touch_session_context(session_id)
        self._prune_contexts()
        
        self.logger.info(f"Nova conversa iniciada: {session_id}")
        return session_id
    
    # Utilitários de segurança
    @staticmethod
    def _sanitize_input(value: str) -> str:
        """
        Remove caracteres perigosos para evitar SQL Injection e outros ataques.
        """
        # isinstance desnecessário, pois value já é str
        return value.replace("'", " ").replace(";", " ").replace("--", " ").replace("/*", " ").replace("*/", " ")

    def _sanitize_log(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove campos sensíveis dos logs.
        """
        sanitized = data.copy()
        for field in self.sensitive_fields:
            if field in sanitized:
                sanitized[field] = '***'
        return sanitized

    # Utilitário de cache
    def _get_doc_cache(self, cache_key: str) -> List[Dict[str, Any]]:
        now = time.time()
        if cache_key in self.doc_cache:
            cached: Dict[str, Any] = self.doc_cache[cache_key]
            if now - cached['ts'] < self.doc_cache_ttl:
                return cached['docs']
        return []

    def _set_doc_cache(self, cache_key: str, docs: List[Dict[str, Any]]):
        self.doc_cache[cache_key] = {'docs': docs, 'ts': time.time()}

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
            # Sanitizar entrada do usuário
            message = self._sanitize_input(message)
            session_id = self._sanitize_input(session_id)
            # Avisar quando OpenAI estiver habilitado mas sem chave; ainda assim prossegue com fallback local
            openai_warning = None
            if self.config.use_openai and not self.config.openai_api_key:
                openai_warning = "⚠️ OPENAI_API_KEY não configurada; responderei em modo local/fallback."

            # Checar conexão com PostgreSQL; se não houver, responder claro ao usuário
            if not self.db_manager.test_connection():
                return {
                    "response": "❌ Não localizei uma instância PostgreSQL ativa. Por favor, instale/inicie o PostgreSQL ou ajuste o DATABASE_URL e tente novamente.",
                    "tokens_used": 0,
                    "response_time": 0.0,
                    "relevant_documents": [],
                    "context_used": False
                }

            # Preparar contexto
            context = []
            
            if use_context and session_id in self.session_contexts:
                context = self.session_contexts[session_id]
            
            # Buscar documentos relevantes se solicitado
            relevant_docs = []
            if search_documents:
                cache_key = f"{message}_{session_id}"
                now = time.time()
                # Verifica cache
                if cache_key in self.doc_cache:
                    cached = self.doc_cache[cache_key]
                    if now - cached['ts'] < self.doc_cache_ttl:
                        relevant_docs = cached['docs']
                if not relevant_docs:
                    relevant_docs = self.embedding_manager.search_similar_documents(
                        message, limit=3, threshold=0.7
                    )
                    self.doc_cache[cache_key] = {'docs': relevant_docs, 'ts': now}
                if relevant_docs:
                    doc_context = "Documentos relevantes encontrados:\n"
                    for i, doc in enumerate(relevant_docs, 1):
                        doc_context += f"{i}. {doc['title']}\n{doc['content']}\n\n"
                    context.append({
                        "role": "system",
                        "content": doc_context
                    })
            
            # Obter resposta da IA
            start_time = time.time()
            response = self.ai_agent.chat(message, session_id, context)
            end_time = time.time()
            self.metrics['messages'] += 1
            self.metrics['response_times'].append(end_time - start_time)

            # Não exibir aviso de fallback local para o usuário final
            # Apenas logar internamente se necessário
            if openai_warning:
                self.logger.warning(f"OPENAI_API_KEY ausente ou inválida. Respondendo em modo local/fallback.")
            
            # Atualizar contexto da sessão
            if use_context:
                self._update_session_context(session_id, message, response["response"])
            
            # Adicionar informações dos documentos à resposta
            response["relevant_documents"] = relevant_docs
            response["context_used"] = len(context) > 0
            
            return response
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem: {e}")
            self.logger.error(f"Dados: {self._sanitize_log({'message': message, 'session_id': session_id})}")
            self.metrics['errors'] += 1
            raise
    
    def _update_session_context(self, session_id: str, user_message: str, ai_response: str, use_context: bool = True, search_documents: bool = True) -> Dict[str, Any]:
        # Função agora apenas atualiza o contexto da sessão
        if session_id in self.session_contexts:
            self.session_contexts[session_id].append({
                "role": "user",
                "content": user_message
            })
            self.session_contexts[session_id].append({
                "role": "ai",
                "content": ai_response
            })
        self._touch_session_context(session_id)
        return {}
    
    def clear_session_context(self, session_id: str):
        """
        Limpa o contexto de uma sessão
        
        Args:
            session_id: ID da sessão
        """
        if session_id in self.session_contexts:
            del self.session_contexts[session_id]
        if session_id in self.session_context_last_used:
            del self.session_context_last_used[session_id]
            self.logger.info(f"Contexto da sessão {session_id} limpo")

    def _touch_session_context(self, session_id: str):
        """Atualiza timestamp de último uso do contexto."""
        self.session_context_last_used[session_id] = time.time()

    def _prune_contexts(self):
        """Remove contextos antigos ou quando ultrapassar o limite total."""
        now = time.time()

        # Remover por TTL
        expired = [sid for sid, ts in self.session_context_last_used.items()
                   if now - ts > self.context_ttl_seconds]
        for sid in expired:
            self.session_contexts.pop(sid, None)
            self.session_context_last_used.pop(sid, None)

        # Se ainda exceder o limite, remover os mais antigos
        if len(self.session_contexts) > self.max_context_sessions:
            ordered = sorted(self.session_context_last_used.items(), key=lambda x: x[1])
            to_remove = len(self.session_contexts) - self.max_context_sessions
            for sid, _ in ordered[:to_remove]:
                self.session_contexts.pop(sid, None)
                self.session_context_last_used.pop(sid, None)
    
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
            
            params: Dict[str, Any] = {"query": f"%{query}%", "limit": limit}
            
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