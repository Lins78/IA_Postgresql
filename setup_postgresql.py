"""
Script de configuração e verificação do PostgreSQL
"""
import subprocess
import sys
import os
import time
import psycopg2
from src.utils.config import Config
from src.utils.logger import setup_logger

class PostgreSQLSetup:
    """Classe para configurar e verificar PostgreSQL"""
    
    def __init__(self):
        self.logger = setup_logger("PostgreSQLSetup", "INFO")
    
    def check_postgresql_installed(self):
        """Verifica se PostgreSQL está instalado"""
        try:
            # Tentar executar psql
            result = subprocess.run(
                ['psql', '--version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                self.logger.info(f"PostgreSQL encontrado: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Verificar diretórios comuns no Windows
        postgres_paths = [
            "C:\\Program Files\\PostgreSQL",
            "C:\\Program Files (x86)\\PostgreSQL",
            "C:\\PostgreSQL"
        ]
        
        for path in postgres_paths:
            if os.path.exists(path):
                self.logger.info(f"PostgreSQL encontrado em: {path}")
                # Tentar adicionar ao PATH
                for root, dirs, files in os.walk(path):
                    if "bin" in dirs:
                        bin_path = os.path.join(root, "bin")
                        if "psql.exe" in os.listdir(bin_path):
                            self.logger.info(f"PostgreSQL bin encontrado: {bin_path}")
                            return True
        
        self.logger.warning("PostgreSQL não encontrado na máquina")
        return False
    
    def check_docker_available(self):
        """Verifica se Docker está disponível"""
        try:
            result = subprocess.run(
                ['docker', '--version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                self.logger.info(f"Docker encontrado: {result.stdout.strip()}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        self.logger.warning("Docker não encontrado")
        return False
    
    def test_connection(self, config):
        """Testa conexão com PostgreSQL"""
        try:
            conn = psycopg2.connect(
                host=config.postgres_host,
                port=config.postgres_port,
                database="postgres",  # Usar database padrão para teste
                user=config.postgres_user,
                password=config.postgres_password
            )
            conn.close()
            self.logger.info("✅ Conexão com PostgreSQL bem-sucedida!")
            return True
        except Exception as e:
            self.logger.error(f"❌ Erro ao conectar: {e}")
            return False
    
    def create_database(self, config):
        """Cria o banco de dados se não existir"""
        try:
            # Conectar ao banco postgres padrão
            conn = psycopg2.connect(
                host=config.postgres_host,
                port=config.postgres_port,
                database="postgres",
                user=config.postgres_user,
                password=config.postgres_password
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Verificar se o banco existe
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (config.postgres_db,)
            )
            
            if cursor.fetchone():
                self.logger.info(f"Banco de dados '{config.postgres_db}' já existe")
            else:
                # Criar o banco
                cursor.execute(f'CREATE DATABASE "{config.postgres_db}"')
                self.logger.info(f"✅ Banco de dados '{config.postgres_db}' criado com sucesso!")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar banco de dados: {e}")
            return False
    
    def setup_postgresql_docker(self):
        """Configura PostgreSQL usando Docker"""
        self.logger.info("Configurando PostgreSQL com Docker...")
        
        try:
            # Verificar se container já existe
            result = subprocess.run(
                ['docker', 'ps', '-a', '--filter', 'name=ia_postgresql', '--format', '{{.Names}}'],
                capture_output=True,
                text=True
            )
            
            if 'ia_postgresql' in result.stdout:
                self.logger.info("Container PostgreSQL já existe. Iniciando...")
                subprocess.run(['docker', 'start', 'ia_postgresql'])
            else:
                self.logger.info("Criando novo container PostgreSQL...")
                cmd = [
                    'docker', 'run', '-d',
                    '--name', 'ia_postgresql',
                    '-e', 'POSTGRES_USER=ia_user',
                    '-e', 'POSTGRES_PASSWORD=ia_password123',
                    '-e', 'POSTGRES_DB=ia_database',
                    '-p', '5432:5432',
                    'postgres:15'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.logger.info("✅ Container PostgreSQL criado e iniciado!")
                    
                    # Aguardar PostgreSQL inicializar
                    self.logger.info("Aguardando PostgreSQL inicializar...")
                    time.sleep(10)
                    
                    return True
                else:
                    self.logger.error(f"❌ Erro ao criar container: {result.stderr}")
                    return False
        
        except Exception as e:
            self.logger.error(f"❌ Erro ao configurar Docker: {e}")
            return False
    
    def interactive_setup(self):
        """Setup interativo para configurar PostgreSQL"""
        print("🐘 CONFIGURAÇÃO DO POSTGRESQL")
        print("=" * 40)
        print()
        
        # Verificar PostgreSQL local
        if self.check_postgresql_installed():
            print("✅ PostgreSQL encontrado na máquina!")
            
            print("\\nConfigurações necessárias:")
            host = input("Host do PostgreSQL [localhost]: ").strip() or "localhost"
            port = input("Porta [5432]: ").strip() or "5432"
            user = input("Usuário do PostgreSQL: ").strip()
            password = input("Senha do PostgreSQL: ").strip()
            database = input("Nome do banco de dados [ia_database]: ").strip() or "ia_database"
            
            # Atualizar arquivo .env
            self.update_env_file(host, port, user, password, database)
            
            # Testar conexão
            config = Config()
            if self.test_connection(config):
                self.create_database(config)
                return True
            else:
                print("❌ Falha na conexão. Verificar credenciais.")
                return False
        
        # Verificar Docker
        elif self.check_docker_available():
            print("✅ Docker disponível!")
            print("\\n🐳 Deseja usar PostgreSQL via Docker? (s/n): ", end="")
            choice = input().lower()
            
            if choice in ['s', 'sim', 'y', 'yes']:
                if self.setup_postgresql_docker():
                    # Configurar .env para Docker
                    self.update_env_file(
                        "localhost", "5432", "ia_user", 
                        "ia_password123", "ia_database"
                    )
                    return True
            else:
                print("❌ Configuração cancelada.")
                return False
        
        # Nenhuma opção disponível
        else:
            print("❌ PostgreSQL não encontrado e Docker não disponível.")
            print("\\nOpções:")
            print("1. Instalar PostgreSQL: https://www.postgresql.org/download/")
            print("2. Instalar Docker: https://www.docker.com/products/docker-desktop")
            print("3. Usar PostgreSQL remoto (ex: ElephantSQL, Heroku)")
            
            print("\\n🌐 Deseja configurar PostgreSQL remoto? (s/n): ", end="")
            choice = input().lower()
            
            if choice in ['s', 'sim', 'y', 'yes']:
                print("\\nConfigurações do PostgreSQL remoto:")
                host = input("Host: ").strip()
                port = input("Porta [5432]: ").strip() or "5432"
                user = input("Usuário: ").strip()
                password = input("Senha: ").strip()
                database = input("Banco de dados: ").strip()
                
                self.update_env_file(host, port, user, password, database)
                
                # Testar conexão
                config = Config()
                return self.test_connection(config)
            
            return False
    
    def update_env_file(self, host, port, user, password, database):
        """Atualiza arquivo .env com configurações do PostgreSQL"""
        env_content = f"""# Configurações da IA conectada ao PostgreSQL
OPENAI_API_KEY=your_openai_api_key_here
POSTGRES_HOST={host}
POSTGRES_PORT={port}
POSTGRES_DB={database}
POSTGRES_USER={user}
POSTGRES_PASSWORD={password}
DATABASE_URL=postgresql://{user}:{password}@{host}:{port}/{database}

# Configurações da aplicação
DEBUG=True
LOG_LEVEL=INFO
MAX_TOKENS=4000
TEMPERATURE=0.7
"""
        
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        
        self.logger.info("✅ Arquivo .env atualizado!")
        print("✅ Arquivo .env atualizado com as configurações do PostgreSQL!")

def main():
    """Função principal de configuração"""
    setup = PostgreSQLSetup()
    
    if setup.interactive_setup():
        print("\\n🎉 PostgreSQL configurado com sucesso!")
        print("Agora você pode executar o sistema:")
        print("  python main.py")
        print("  streamlit run examples/streamlit_app.py")
        return 0
    else:
        print("\\n❌ Falha na configuração do PostgreSQL")
        return 1

if __name__ == "__main__":
    exit(main())