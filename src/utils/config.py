"""
Gerenciador de configurações para a IA PostgreSQL
"""
import os
from dotenv import load_dotenv
from typing import Optional

class Config:
    """Classe para gerenciar configurações da aplicação"""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Inicializa as configurações
        
        Args:
            env_file: Caminho para o arquivo .env (opcional)
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # Configurações do OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_openai = os.getenv("USE_OPENAI", "true").lower() == "true"
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.openai_timeout = float(os.getenv("OPENAI_TIMEOUT", 30))
        
        # Configurações do PostgreSQL
        self.postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        self.postgres_port = int(os.getenv("POSTGRES_PORT", 5432))
        self.postgres_db = os.getenv("POSTGRES_DB", "ia_database")
        self.postgres_user = os.getenv("POSTGRES_USER")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD")
        
        # URL completa do banco
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url and all([self.postgres_user, self.postgres_password]):
            self.database_url = (
                f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        
        # Configurações da aplicação
        self.ai_name = os.getenv("AI_NAME", "Mamute")
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.max_tokens = int(os.getenv("MAX_TOKENS", 4000))
        self.temperature = float(os.getenv("TEMPERATURE", 0.7))

        # Segurança / API
        self.api_key = os.getenv("API_KEY")

        # CORS
        allowed_origins_env = os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:8002,http://127.0.0.1:8002"
        )
        self.allowed_origins = [o.strip() for o in allowed_origins_env.split(',') if o.strip()]
        self.allow_cors_credentials = os.getenv("ALLOW_CORS_CREDENTIALS", "false").lower() == "true"
    
    def validate(self, check_openai: bool = True) -> bool:
        """
        Valida se as configurações essenciais estão presentes
        
        Args:
            check_openai: Se deve verificar a chave da OpenAI
        
        Returns:
            bool: True se todas as configurações estão válidas
        """
        required_configs = []
        
        # Sempre verificar banco de dados
        if not self.database_url:
            required_configs.append("DATABASE_URL ou credenciais do PostgreSQL")
        
        # Verificar OpenAI apenas se solicitado e habilitado
        if check_openai and self.use_openai and not self.openai_api_key:
            required_configs.append("OPENAI_API_KEY")
        
        if required_configs:
            raise ValueError(
                f"Configurações obrigatórias não encontradas: {', '.join(required_configs)}"
            )
        
        return True
    
    def validate_database_only(self) -> bool:
        """
        Valida apenas as configurações do banco de dados
        
        Returns:
            bool: True se as configurações do banco estão válidas
        """
        return self.validate(check_openai=False)