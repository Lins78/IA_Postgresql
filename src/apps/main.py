"""
Sistema de IA conectada ao PostgreSQL
Arquivo principal para inicialização e execução
"""
import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path (arquivo está em src/apps)
SRC_DIR = Path(__file__).resolve().parents[1]
APPS_DIR = SRC_DIR / "apps"
for path in (SRC_DIR, APPS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.database.connection import DatabaseManager
from src.ai.agent import AIAgent
from src.ai.embeddings import EmbeddingManager
from src.ai.chat import ChatManager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importar sistema de personalidade
try:
    from mamute_chat_personality import MamuteChatPersonality
    PERSONALITY_AVAILABLE = True
except ImportError:
    PERSONALITY_AVAILABLE = False

class IAPostgreSQL:
    """Classe principal para o sistema de IA conectada ao PostgreSQL"""
    
    def __init__(self, env_file: str = ".env"):
        """
        Inicializa o sistema
        
        Args:
            env_file: Caminho para o arquivo de configuração
        """
        # Carregar configurações
        self.config = Config(env_file)
        self.config.validate()
        
        # Setup logger
        self.logger = setup_logger("IAPostgreSQL", self.config.log_level)
        
        # Inicializar componentes
        self.db_manager = DatabaseManager(self.config)
        # Criar manager separado para operações da IA usando credenciais específicas (se existirem)
        from sqlalchemy.engine import make_url
        ai_db_manager = None
        ai_user = os.getenv('AI_DB_USER')
        ai_pass = os.getenv('AI_DB_PASSWORD')
        if ai_user and ai_pass:
            try:
                parsed = make_url(self.config.database_url)
                new_url = parsed.set(username=ai_user, password=ai_pass)
                ai_db_manager = DatabaseManager(self.config)
                ai_db_manager.engine = create_engine(str(new_url), echo=self.config.debug, pool_size=10, max_overflow=20)
                ai_db_manager.Session = sessionmaker(bind=ai_db_manager.engine)
                self.logger.info('AI DatabaseManager criado com credenciais AI_DB_USER')
            except Exception as e:
                self.logger.warning(f'Falha ao criar AI DatabaseManager: {e}')

        if not ai_db_manager:
            ai_db_manager = self.db_manager
        # Expor o manager usado pela IA para operações com credenciais AI
        self.ai_db_manager = ai_db_manager
        self.ai_agent = AIAgent(self.config, ai_db_manager)
        self.embedding_manager = EmbeddingManager(self.config, ai_db_manager)
        self.chat_manager = ChatManager(
            self.config, 
            self.db_manager, 
            self.ai_agent, 
            self.embedding_manager
        )
        
        # Inicializar sistema de personalidade se disponível
        self.chat_personality = None
        if PERSONALITY_AVAILABLE:
            try:
                self.chat_personality = MamuteChatPersonality(env_file)
                self.logger.info("🎭 Sistema de personalidade inicializado com sucesso")
            except Exception as e:
                self.logger.warning(f"Não foi possível inicializar personalidade: {e}")
        
        self.logger.info("Sistema de IA PostgreSQL inicializado com sucesso")
    
    def setup_database(self):
        """Configura o banco de dados (cria tabelas e ajusta esquema faltante)"""
        try:
            if not self.db_manager.test_connection():
                raise ConnectionError("Não foi possível conectar ao PostgreSQL")
            
            self.db_manager.create_tables()
            self.db_manager.ensure_schema_columns()
            self.logger.info("Banco de dados configurado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao configurar banco de dados: {e}")
            raise
    
    def start_conversation(self, user_id: str = None) -> str:
        """
        Inicia uma nova conversa
        
        Args:
            user_id: ID do usuário (opcional)
        
        Returns:
            str: ID da sessão
        """
        return self.chat_manager.start_conversation(user_id)
    
    def chat(self, message: str, session_id: str) -> dict:
        """
        Envia mensagem para a IA
        
        Args:
            message: Mensagem do usuário
            session_id: ID da sessão
        
        Returns:
            dict: Resposta da IA
        """
        return self.chat_manager.send_message(message, session_id)
    
    def add_document(self, title: str, content: str, **kwargs) -> int:
        """
        Adiciona documento ao sistema
        
        Args:
            title: Título do documento
            content: Conteúdo do documento
            **kwargs: Argumentos adicionais
        
        Returns:
            int: ID do documento criado
        """
        return self.embedding_manager.add_document(title, content, **kwargs)
    
    def analyze_table(self, table_name: str) -> dict:
        """
        Analisa uma tabela do banco de dados
        
        Args:
            table_name: Nome da tabela
        
        Returns:
            dict: Resultado da análise
        """
        return self.ai_agent.analyze_data(table_name)

def main():
    """Função principal para demonstração"""
    try:
        # Inicializar sistema
        ia_system = IAPostgreSQL()
        
        # Configurar banco de dados
        print("Configurando banco de dados...")
        ia_system.setup_database()
        
        # Exemplo de uso
        print("\\n=== Exemplo de Conversa ===")
        
        # Iniciar conversa
        session_id = ia_system.start_conversation("usuario_demo")
        print(f"Sessão iniciada: {session_id}")
        
        # Enviar mensagem
        messages = [
            "Olá! Como você pode me ajudar?",
            "Quais tabelas estão disponíveis no banco de dados?",
            "Pode fazer uma análise da tabela user_sessions?"
        ]
        
        for msg in messages:
            print(f"\\n👤 Usuário: {msg}")
            response = ia_system.chat(msg, session_id)
            print(f"🐘 Mamute: {response['response']}")
            print(f"   (Tokens: {response['tokens_used']}, Tempo: {response['response_time']:.2f}s)")
        
        print("\\n=== Exemplo Concluído ===")
        
    except Exception as e:
        print(f"Erro: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())