"""
Sistema de IA conectada ao PostgreSQL
Arquivo principal para inicialização e execução
"""
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.database.connection import DatabaseManager
from src.ai.agent import AIAgent
from src.ai.embeddings import EmbeddingManager
from src.ai.chat import ChatManager

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
        self.ai_agent = AIAgent(self.config, self.db_manager)
        self.embedding_manager = EmbeddingManager(self.config, self.db_manager)
        self.chat_manager = ChatManager(
            self.config, 
            self.db_manager, 
            self.ai_agent, 
            self.embedding_manager
        )
        
        self.logger.info("Sistema de IA PostgreSQL inicializado com sucesso")
    
    def setup_database(self):
        """Configura o banco de dados (cria tabelas)"""
        try:
            if not self.db_manager.test_connection():
                raise ConnectionError("Não foi possível conectar ao PostgreSQL")
            
            self.db_manager.create_tables()
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