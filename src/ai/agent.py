"""
Agente principal de IA
"""
import time
import uuid
from typing import Dict, List, Any, Optional

import openai

from ..database.connection import DatabaseManager
from ..database.models import Conversation, UserSession
from ..utils.config import Config
from ..utils.logger import setup_logger

# Guia compacto para orientar respostas de PostgreSQL quando usar modelos LLM
POSTGRES_CHEAT_SHEET = (
    "Responda como especialista PostgreSQL. Inclua exemplos SQL quando útil.\n"
    "Introspecao: listar bancos (SELECT datname FROM pg_database WHERE datistemplate=false ORDER BY datname); "
    "trocar no psql (\\c nome_db); listar tabelas (SELECT table_name FROM information_schema.tables WHERE table_schema='public'); "
    "colunas (SELECT column_name,data_type,is_nullable,column_default FROM information_schema.columns WHERE table_schema='public' AND table_name='<tabela>').\n"
    "Consultas: SELECT ... WHERE ... ORDER BY ... LIMIT ...; JOINs (INNER/LEFT/RIGHT/FULL) usando ON; agregacoes COUNT/SUM/AVG/MIN/MAX com GROUP BY e HAVING.\n"
    "DML: INSERT INTO t(cols) VALUES (...); UPDATE t SET col=... WHERE ...; DELETE FROM t WHERE ...; UPSERT com INSERT ... ON CONFLICT (pk) DO UPDATE SET ....\n"
    "DDL: CREATE TABLE com tipos (serial/bigserial, varchar, numeric, timestamptz, jsonb); constraints (PRIMARY KEY, UNIQUE, CHECK, FOREIGN KEY). ALTER TABLE ADD COLUMN/ALTER TYPE; DROP TABLE.\n"
    "Indices: CREATE INDEX idx ON t(col); indice composto; UNIQUE; verifica indices em pg_indexes; uso do EXPLAIN (ANALYZE, BUFFERS) para performance.\n"
    "Performance: evitar SELECT * em tabelas grandes; filtros por colunas indexadas; VACUUM/ANALYZE; REINDEX; ajuste de LIMIT para exploracao; observar cache hit em pg_stat_database e pg_stat_statements.\n"
    "Backup/restore: pg_dump -Fc db > file; pg_restore -d db file; para tabela especifica use -t; para apenas schema use --schema-only.\n"
    "Permissoes: CREATE ROLE; GRANT CONNECT/USAGE/SELECT/INSERT/UPDATE/DELETE em schemas e tabelas; verificar roles com \"\"\"SELECT rolname, rolsuper, rolcreaterole, rolcreatedb FROM pg_roles;\"\"\".\n"
    "Tipos e funcoes: datas (NOW, AGE, EXTRACT), strings (UPPER, CONCAT), arrays (unnest), JSONB (->, ->>, @>), window functions (ROW_NUMBER, PARTITION BY).\n"
    "Admin: tamanho de tabelas (pg_total_relation_size), conexoes (pg_stat_activity), locks (pg_locks join pg_class), variaveis (SHOW ALL).\n"
)


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
        self.use_openai = config.use_openai and bool(config.openai_api_key)
        self.api_key = config.openai_api_key
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key) if self.use_openai else None

        # Parâmetros do modelo
        self.model_name = config.openai_model
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature
        self.request_timeout = getattr(config, "openai_timeout", 30)

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

    def chat(self, message: str, session_id: str, context: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
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
            if self.client is not None and self.api_key and self.use_openai:
                try:
                    # Usar OpenAI
                    return self._chat_with_openai(message, session_id, context, start_time)
                except Exception:
                    # Falha de OpenAI (inclui chave inválida/401). Fazer fallback seguro sem expor detalhes sensíveis.
                    self.logger.error("Erro no OpenAI, alternando para fallback (detalhes ocultos).")
                    self.use_openai = False  # evita tentar novamente nesta instância
                    fallback_result = self._chat_fallback(message, session_id, start_time)
                    fallback_result["response"] = (
                        "⚠️ Não consegui usar o modelo OpenAI (chave inválida ou indisponível). "
                        "Responderei em modo local.\n\n" + fallback_result["response"]
                    )
                    fallback_result["error"] = True
                    return fallback_result
            else:
                reason = "OpenAI desabilitado" if not self.use_openai else "OpenAI sem chave" if not self.api_key else "Cliente OpenAI indisponível"
                self.logger.info(f"Usando fallback local ({reason}) para sessão {session_id}")
                # Usar sistema de fallback inteligente
                return self._chat_fallback(message, session_id, start_time)

        except Exception as e:
            self.logger.error(f"Erro no chat: {e}")
            response_time = time.time() - start_time

            # Retornar resposta de erro
            return {
                "response": "Desculpe, não foi possível processar sua mensagem agora. Estou em modo local e o erro foi registrado.",
                "tokens_used": 0,
                "response_time": response_time,
                "session_id": session_id,
                "error": True
            }

    def _prepare_messages(self, user_message: str, context: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, str]]:
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
                    f"Você é {self.config.ai_name}, um assistente de IA especializado em PostgreSQL. "
                    "Seja preciso e seguro: explique, dê exemplos SQL, proponha passos claros. "
                    "Use o guia interno abaixo para responder perguntas sobre funcionalidades do PostgreSQL, "
                    "incluindo DDL, DML, índices, performance, backups, permissões, JSONB, window functions e introspecção do catálogo.\n\n"
                    f"Guia rápido PostgreSQL:\n{POSTGRES_CHEAT_SHEET}"
                )
            }
        ]

        # Adicionar contexto se fornecido
        if context:
            for ctx in context[-5:]:  # Manter apenas os últimos 5 contextos
                messages.append(dict(ctx))

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
            # Detectar coluna ausente e tentar corrigi-la automaticamente
            msg = str(e)
            self.logger.error(f"Erro ao salvar conversa: {e}")
            try:
                if 'created_at' in msg or 'UndefinedColumn' in msg:
                    self.logger.warning('Coluna created_at ausente detectada. Tentando adicionar coluna...')
                    try:
                        self.db_manager.execute_command(
                            "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();"
                        )
                        self.logger.info('Coluna created_at adicionada com sucesso. Re-tentando salvar conversa...')
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
                            return
                    except Exception as fix_e:
                        self.logger.error(f'Falha ao tentar adicionar coluna created_at: {fix_e}')
            except Exception:
                pass

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
            # Garantir que o identificador é seguro e que a tabela existe
            self.db_manager.assert_valid_identifier(table_name)
            tables = self.db_manager.get_all_tables()
            if table_name not in tables:
                raise ValueError(f"Tabela '{table_name}' não encontrada")

            # Obter informações da tabela
            table_info = self.db_manager.get_table_info(table_name)

            if analysis_type == "summary":
                count_query = f'SELECT COUNT(*) as total_rows FROM "{table_name}"'
                count_result = self.db_manager.execute_query(count_query)

                sample_query = f'SELECT * FROM "{table_name}" LIMIT 5'
                sample_result = self.db_manager.execute_query(sample_query)

                result: Dict[str, Any] = {
                    "table_name": table_name,
                    "columns": table_info,
                    "total_rows": count_result[0]['total_rows'],
                    "sample_data": sample_result
                }
                return result
            else:
                return {"error": f"Tipo de análise '{analysis_type}' não suportado."}
        except Exception as e:
            self.logger.error(f"Erro na análise de dados: {e}")
            return {"error": str(e)}

    def _chat_with_openai(self, message: str, session_id: str, context: Optional[List[Dict[str, Any]]], start_time: float) -> Dict[str, Any]:
        """Chat usando OpenAI API"""
        # Preparar mensagens para o modelo
        messages = self._prepare_messages(message, context)

        # Chamar a API do OpenAI
        if self.client is None:
            return {"error": "Cliente OpenAI não configurado."}

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,  # type: ignore
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            timeout=self.request_timeout
        )

        # Extrair resposta
        ai_response = getattr(response.choices[0].message, "content", "")
        tokens_used = getattr(getattr(response, "usage", None), "total_tokens", 0)
        response_time = time.time() - start_time

        # Salvar conversa no banco
        self._save_conversation(
            session_id=session_id,
            user_message=message,
            ai_response=ai_response or "",
            tokens_used=tokens_used,
            response_time=response_time
        )

        # Atualizar estatísticas da sessão
        self._update_session_stats(session_id, tokens_used)

        result: Dict[str, Any] = {
            "response": ai_response or "",
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
