#!/usr/bin/env python3
"""
🛠️ CONFIGURADOR AUTOMÁTICO - MAMUTE SEMPRE ONLINE
Detecta e corrige automaticamente problemas de configuração
"""

import os
import sys
import json
import subprocess
import psutil
import requests
from pathlib import Path
import getpass
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MamuteAutoConfigurator:
    """Configurador automático do sistema Mamute"""
    
    def __init__(self):
        self.project_path = Path(__file__).parent
        self.config_file = self.project_path / "mamute_config.json"
        
    def detect_postgresql(self):
        """Detectar instalação PostgreSQL"""
        logger.info("🔍 Detectando PostgreSQL...")
        
        # Caminhos comuns do PostgreSQL
        common_paths = [
            "C:/PostgreSQL",
            "C:/Program Files/PostgreSQL", 
            "C:/Program Files (x86)/PostgreSQL",
            "C:/PostgreSql"
        ]
        
        postgres_paths = []
        
        for base_path in common_paths:
            if os.path.exists(base_path):
                for item in os.listdir(base_path):
                    full_path = os.path.join(base_path, item)
                    if os.path.isdir(full_path):
                        bin_path = os.path.join(full_path, "bin")
                        if os.path.exists(bin_path) and os.path.exists(os.path.join(bin_path, "postgres.exe")):
                            postgres_paths.append(bin_path)
        
        if postgres_paths:
            logger.info(f"✅ PostgreSQL encontrado: {postgres_paths[0]}")
            return postgres_paths[0]
        else:
            logger.error("❌ PostgreSQL não encontrado")
            return None
    
    def check_postgresql_service(self):
        """Verificar se serviço PostgreSQL está rodando"""
        logger.info("🔍 Verificando serviço PostgreSQL...")
        
        try:
            # Verificar processos PostgreSQL
            for proc in psutil.process_iter(['pid', 'name']):
                if 'postgres' in proc.info['name'].lower():
                    logger.info(f"✅ PostgreSQL rodando: PID {proc.info['pid']}")
                    return True
                    
            # Tentar iniciar serviço se não estiver rodando
            logger.info("⚠️ PostgreSQL não está rodando, tentando iniciar...")
            
            # Windows
            if os.name == 'nt':
                services = [
                    "postgresql-x64-14",
                    "postgresql-x64-13", 
                    "postgresql-x64-12",
                    "postgresql-9.4",
                    "PostgreSQL"
                ]
                
                for service in services:
                    try:
                        result = subprocess.run(
                            ["sc", "start", service],
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            logger.info(f"✅ Serviço {service} iniciado")
                            return True
                    except:
                        continue
            
            logger.error("❌ Não foi possível iniciar PostgreSQL")
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar PostgreSQL: {e}")
            return False
    
    def test_postgresql_connection(self, config):
        """Testar conexão com PostgreSQL"""
        logger.info("🧪 Testando conexão PostgreSQL...")
        
        try:
            import psycopg2
            
            conn = psycopg2.connect(
                host=config["host"],
                port=config["port"],
                user=config["user"],
                password=config["password"],
                database="postgres"
            )
            conn.close()
            logger.info("✅ Conexão PostgreSQL: OK")
            return True
            
        except psycopg2.OperationalError as e:
            logger.error(f"❌ Erro de conexão: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}")
            return False
    
    def auto_configure_postgresql(self):
        """Configurar PostgreSQL automaticamente"""
        logger.info("⚙️ Configurando PostgreSQL automaticamente...")
        
        # Configurações para testar
        test_configs = [
            {"host": "localhost", "port": "5432", "user": "postgres", "password": ""},
            {"host": "localhost", "port": "5432", "user": "postgres", "password": "postgres"},
            {"host": "localhost", "port": "5432", "user": "postgres", "password": "admin"},
            {"host": "localhost", "port": "5432", "user": "postgres", "password": "postgres@"},
            {"host": "localhost", "port": "5432", "user": "postgres", "password": "123456"}
        ]
        
        for config in test_configs:
            logger.info(f"   Testando: {config['user']}@{config['host']}:{config['port']}")
            if self.test_postgresql_connection(config):
                logger.info(f"✅ Configuração válida encontrada: {config}")
                return config
        
        # Se nenhuma configuração automática funcionou, pedir ao usuário
        logger.info("🔐 Configuração manual necessária")
        print("\n" + "="*50)
        print("🔐 CONFIGURAÇÃO MANUAL POSTGRESQL")
        print("="*50)
        
        config = {
            "host": input("Host [localhost]: ").strip() or "localhost",
            "port": input("Porta [5432]: ").strip() or "5432",
            "user": input("Usuário [postgres]: ").strip() or "postgres",
            "password": getpass.getpass("Senha: ").strip()
        }
        
        if self.test_postgresql_connection(config):
            logger.info("✅ Configuração manual válida")
            return config
        else:
            logger.error("❌ Configuração manual inválida")
            return None
    
    def setup_database(self, pg_config):
        """Configurar banco de dados IA"""
        logger.info("💾 Configurando banco de dados IA...")
        
        try:
            import psycopg2
            
            # Conectar como admin
            admin_conn = psycopg2.connect(
                host=pg_config["host"],
                port=pg_config["port"],
                user=pg_config["user"],
                password=pg_config["password"],
                database="postgres"
            )
            admin_conn.autocommit = True
            cursor = admin_conn.cursor()
            
            # Verificar se banco existe
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'ia_database'")
            if cursor.fetchone():
                logger.info("✅ Banco 'ia_database' já existe")
            else:
                cursor.execute("CREATE DATABASE ia_database")
                logger.info("✅ Banco 'ia_database' criado")
            
            cursor.close()
            admin_conn.close()
            
            # Adicionar banco à configuração
            pg_config["database"] = "ia_database"
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar banco: {e}")
            return False
    
    def check_dependencies(self):
        """Verificar dependências Python"""
        logger.info("📦 Verificando dependências...")
        
        required_packages = [
            "fastapi",
            "uvicorn",
            "psycopg2-binary",
            "requests",
            "psutil"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.info(f"📦 Instalando pacotes faltantes: {missing_packages}")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install"
                ] + missing_packages, check=True)
                logger.info("✅ Dependências instaladas")
                return True
            except Exception as e:
                logger.error(f"❌ Erro ao instalar dependências: {e}")
                return False
        else:
            logger.info("✅ Todas as dependências estão instaladas")
            return True
    
    def check_tunnel_tools(self):
        """Verificar ferramentas de túnel"""
        logger.info("🌍 Verificando ferramentas de túnel...")
        
        tools = {
            "ngrok": self.check_ngrok(),
            "cloudflared": self.check_cloudflared(),
            "ssh": self.check_ssh()
        }
        
        available_tools = [tool for tool, available in tools.items() if available]
        
        if available_tools:
            logger.info(f"✅ Túneis disponíveis: {', '.join(available_tools)}")
            return available_tools
        else:
            logger.warning("⚠️ Nenhuma ferramenta de túnel disponível")
            return []
    
    def check_ngrok(self):
        """Verificar se ngrok está disponível"""
        try:
            result = subprocess.run(["ngrok", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("   ✅ ngrok disponível")
                return True
        except:
            pass
        logger.info("   ❌ ngrok não encontrado")
        return False
    
    def check_cloudflared(self):
        """Verificar se cloudflared está disponível"""
        cloudflared_path = self.project_path / "cloudflared.exe"
        if cloudflared_path.exists():
            logger.info("   ✅ cloudflared disponível")
            return True
        logger.info("   ❌ cloudflared não encontrado")
        return False
    
    def check_ssh(self):
        """Verificar se SSH está disponível"""
        try:
            result = subprocess.run(["ssh", "-V"], 
                                  capture_output=True, text=True)
            logger.info("   ✅ ssh disponível")
            return True
        except:
            pass
        logger.info("   ❌ ssh não encontrado")
        return False
    
    def create_configuration(self, pg_config, tunnel_tools):
        """Criar configuração final"""
        logger.info("📝 Criando configuração final...")
        
        config = {
            "postgres": pg_config,
            "server": {
                "port": 8000,
                "host": "0.0.0.0"
            },
            "tunnels": {
                "preferred": tunnel_tools[0] if tunnel_tools else "none",
                "fallback": tunnel_tools[1:] if len(tunnel_tools) > 1 else []
            },
            "monitoring": {
                "health_check_interval": 30,
                "max_restart_attempts": 5,
                "auto_recovery": True
            }
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Configuração salva: {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar configuração: {e}")
            return False
    
    def create_env_file(self, pg_config):
        """Criar arquivo .env"""
        logger.info("📝 Criando arquivo .env...")
        
        env_content = f"""# Configuração Mamute - Gerada automaticamente
DATABASE_URL=postgresql://{pg_config['user']}:{pg_config['password']}@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}
POSTGRES_HOST={pg_config['host']}
POSTGRES_PORT={pg_config['port']}
POSTGRES_DB={pg_config['database']}
POSTGRES_USER={pg_config['user']}
POSTGRES_PASSWORD={pg_config['password']}

# Configurações da aplicação
AI_NAME=Mamute
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

# API Keys (configure se necessário)
OPENAI_API_KEY=your_openai_api_key_here
"""
        
        try:
            env_file = self.project_path / ".env"
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            logger.info(f"✅ Arquivo .env criado: {env_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao criar .env: {e}")
            return False
    
    def run_configuration(self):
        """Executar configuração completa"""
        print("🛠️ CONFIGURADOR AUTOMÁTICO MAMUTE")
        print("=" * 50)
        print("✅ Detecção automática de configurações")
        print("✅ Configuração PostgreSQL")
        print("✅ Verificação de dependências")
        print("✅ Configuração de túneis")
        print("=" * 50)
        print()
        
        # 1. Detectar PostgreSQL
        postgres_path = self.detect_postgresql()
        if not postgres_path:
            logger.error("❌ PostgreSQL não encontrado. Instale PostgreSQL primeiro.")
            return False
        
        # 2. Verificar serviço
        if not self.check_postgresql_service():
            logger.error("❌ Serviço PostgreSQL não está rodando")
            return False
        
        # 3. Verificar dependências
        if not self.check_dependencies():
            logger.error("❌ Falha na verificação de dependências")
            return False
        
        # 4. Configurar PostgreSQL
        pg_config = self.auto_configure_postgresql()
        if not pg_config:
            logger.error("❌ Falha na configuração PostgreSQL")
            return False
        
        # 5. Configurar banco de dados
        if not self.setup_database(pg_config):
            logger.error("❌ Falha na configuração do banco")
            return False
        
        # 6. Verificar túneis
        tunnel_tools = self.check_tunnel_tools()
        
        # 7. Criar configuração
        if not self.create_configuration(pg_config, tunnel_tools):
            logger.error("❌ Falha ao criar configuração")
            return False
        
        # 8. Criar arquivo .env
        if not self.create_env_file(pg_config):
            logger.error("❌ Falha ao criar .env")
            return False
        
        print("\n" + "=" * 50)
        print("✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 50)
        print(f"🐘 PostgreSQL: {pg_config['host']}:{pg_config['port']}")
        print(f"💾 Banco: {pg_config['database']}")
        print(f"🌍 Túneis: {', '.join(tunnel_tools) if tunnel_tools else 'Nenhum'}")
        print("📝 Configuração: mamute_config.json")
        print("🔧 Variáveis: .env")
        print("=" * 50)
        print()
        print("🚀 Execute: python sistema_conexao_definitivo.py")
        print()
        
        return True


def main():
    """Função principal"""
    configurator = MamuteAutoConfigurator()
    
    try:
        success = configurator.run_configuration()
        return success
    except KeyboardInterrupt:
        logger.info("🛑 Configuração cancelada pelo usuário")
        return False
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)