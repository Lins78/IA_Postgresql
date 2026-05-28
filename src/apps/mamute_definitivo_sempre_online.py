#!/usr/bin/env python3
"""
🚀 SISTEMA DEFINITIVO MAMUTE - SEMPRE ONLINE 24/7
Sistema ultra-robusto que garante 100% de disponibilidade
"""

import subprocess
import time
import requests
import os
import sys
import threading
import psutil
import json
import logging
import signal
import asyncio
import socket
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import webbrowser
import traceback

# Configurar logging
log_file = Path("mamute_definitivo.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MamuteDefinitivo")

class SistemaDefinitivoMamute:
    """Sistema definitivo que mantém o Mamute sempre online"""
    
    def __init__(self):
        # Carregar configurações
        self.load_config()
        
        self.port = self.config["server"]["primary_port"]
        self.backup_ports = self.config["server"]["backup_ports"]
        self.server_process = None
        self.tunnel_process = None
        self.is_running = True
        self.restart_count = 0
        self.last_health_check = datetime.now()
        
        # Configurar variáveis de ambiente
        self.setup_environment()
        
        # Configurar handlers para shutdown gracioso
        signal.signal(signal.SIGINT, self.shutdown_handler)
        signal.signal(signal.SIGTERM, self.shutdown_handler)
    
    def load_config(self):
        """Carregar configurações do arquivo JSON"""
        config_file = Path("mamute_config_definitivo.json")
        
        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info("✅ Configuração carregada do arquivo")
            else:
                # Configuração padrão se arquivo não existir
                self.config = self.get_default_config()
                self.save_config()
                logger.info("📝 Arquivo de configuração criado com valores padrão")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar configuração: {e}")
            self.config = self.get_default_config()
    
    def get_default_config(self):
        """Retornar configuração padrão"""
        return {
            "system": {
                "auto_open_browser": True,
                "enable_tunnel": True,
                "health_check_interval": 15,
                "restart_threshold": 3,
                "max_restart_attempts": 999999
            },
            "server": {
                "primary_port": 8001,
                "backup_ports": [8002, 8003, 8004, 8005],
                "host": "0.0.0.0"
            },
            "database": {
                "host": "localhost",
                "port": "5432",
                "database": "ia_database",
                "user": "postgres",
                "password": "postgres@"
            },
            "tunnels": {
                "enabled_providers": ["ngrok", "cloudflare", "serveo"],
                "preferred_provider": "ngrok"
            },
            "monitoring": {
                "log_level": "INFO",
                "log_file": "mamute_definitivo.log",
                "enable_metrics": True,
                "enable_alerts": True
            },
            "recovery": {
                "enable_auto_recovery": True,
                "recovery_delay": 5,
                "cleanup_before_restart": True,
                "kill_conflicting_processes": True
            }
        }
    
    def save_config(self):
        """Salvar configuração no arquivo"""
        try:
            config_file = Path("mamute_config_definitivo.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar configuração: {e}")
    
    def setup_environment(self):
        """Configurar todas as variáveis de ambiente necessárias"""
        db_config = self.config["database"]
        database_url = f"postgresql://{db_config['user']}:{db_config['password'].replace('@', '%40')}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        
        env_vars = {
            "POSTGRES_HOST": db_config["host"],
            "POSTGRES_PORT": db_config["port"], 
            "POSTGRES_DB": db_config["database"],
            "POSTGRES_USER": db_config["user"],
            "POSTGRES_PASSWORD": db_config["password"],
            "DATABASE_URL": database_url,
            "AI_NAME": "Mamute",
            "PYTHONPATH": str(Path.cwd()),
            "PYTHONIOENCODING": "utf-8"
        }
        
        for key, value in env_vars.items():
            os.environ[key] = value
    
    def is_port_free(self, port: int) -> bool:
        """Verificar se a porta está livre"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result != 0
        except:
            return False
    
    def kill_process_on_port(self, port: int):
        """Matar processo usando a porta especificada"""
        try:
            for proc in psutil.process_iter(['pid', 'connections']):
                try:
                    connections = proc.info['connections']
                    if connections:
                        for conn in connections:
                            if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port:
                                logger.info(f"🔄 Terminando processo {proc.pid} na porta {port}")
                                proc.terminate()
                                proc.wait(timeout=5)
                                return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            logger.warning(f"Erro ao matar processo na porta {port}: {e}")
        return False
    
    def find_available_port(self) -> int:
        """Encontrar uma porta disponível"""
        # Tentar porta principal primeiro
        if self.is_port_free(self.port):
            return self.port
        
        # Se não estiver livre, matar o processo
        logger.info(f"🔄 Porta {self.port} ocupada, liberando...")
        if self.kill_process_on_port(self.port):
            time.sleep(2)
            if self.is_port_free(self.port):
                return self.port
        
        # Tentar portas backup
        for port in self.backup_ports:
            if self.is_port_free(port):
                logger.info(f"✅ Usando porta backup: {port}")
                return port
        
        # Se nenhuma porta estiver livre, forçar limpeza
        logger.warning("🧹 Forçando limpeza de todas as portas...")
        for port in [self.port] + self.backup_ports:
            self.kill_process_on_port(port)
        
        time.sleep(3)
        return self.port
    
    def test_database_connection(self) -> bool:
        """Testar conexão com banco de dados"""
        try:
            import psycopg2
            db_config = self.config["database"]
            conn = psycopg2.connect(
                host=db_config["host"],
                port=db_config["port"],
                database=db_config["database"],
                user=db_config["user"], 
                password=db_config["password"],
                connect_timeout=5
            )
            conn.close()
            logger.info("✅ Conexão com banco de dados OK")
            return True
        except Exception as e:
            logger.error(f"❌ Erro na conexão com banco: {e}")
            return False
    
    def start_web_server(self, port: int) -> Optional[subprocess.Popen]:
        """Iniciar servidor web na porta especificada"""
        try:
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "web_app:app",
                "--host", self.config["server"]["host"],
                "--port", str(port),
                "--access-log"
            ]
            
            logger.info(f"🚀 Iniciando servidor na porta {port}...")

            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            server_log = open(logs_dir / "web_server_definitivo.log", "a", encoding="utf-8")
            
            process = subprocess.Popen(
                cmd,
                stdout=server_log,
                stderr=server_log,
                env=os.environ.copy(),
                bufsize=1,
            )
            
            # Aguardar inicialização
            for attempt in range(60):  # até 60 segundos
                time.sleep(1)
                
                if process.poll() is not None:
                    logger.error("❌ Processo do servidor terminou inesperadamente")
                    return None
                
                if self.test_server_health(port):
                    logger.info(f"✅ Servidor iniciado com sucesso na porta {port}")
                    return process
            
            logger.error("❌ Timeout ao iniciar servidor")
            process.terminate()
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar servidor: {e}")
            traceback.print_exc()
            return None
    
    def test_server_health(self, port: int) -> bool:
        """Testar se o servidor está respondendo"""
        try:
            response = requests.get(
                f"http://localhost:{port}/health",
                timeout=3
            )
            return response.status_code == 200
        except:
            try:
                # Testar rota principal se /health não existir
                response = requests.get(
                    f"http://localhost:{port}/",
                    timeout=3
                )
                return response.status_code in [200, 404]  # 404 também indica que o servidor está respondendo
            except:
                return False
    
    def start_tunnel(self, port: int):
        """Iniciar túnel para acesso externo"""
        if not self.config["system"]["enable_tunnel"]:
            return
        
        enabled_providers = self.config["tunnels"]["enabled_providers"]
        preferred = self.config["tunnels"]["preferred_provider"]
        
        # Tentar provider preferido primeiro
        if preferred in enabled_providers:
            providers = [preferred] + [p for p in enabled_providers if p != preferred]
        else:
            providers = enabled_providers
        
        for provider in providers:
            try:
                if provider == "ngrok":
                    logger.info("🌐 Tentando túnel ngrok...")
                    process = subprocess.Popen(
                        ['ngrok', 'http', str(port), '--log=stdout'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                    
                elif provider == "cloudflare":
                    logger.info("☁️ Tentando Cloudflare Tunnel...")
                    process = subprocess.Popen(
                        ['cloudflared', 'tunnel', '--url', f'http://localhost:{port}'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                    
                elif provider == "serveo":
                    logger.info("🔗 Tentando Serveo...")
                    process = subprocess.Popen(
                        ['ssh', '-R', f'80:localhost:{port}', 'serveo.net'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                
                time.sleep(3)
                if process.poll() is None:
                    self.tunnel_process = process
                    logger.info(f"✅ Túnel {provider} iniciado com sucesso!")
                    return
                    
            except FileNotFoundError:
                logger.warning(f"⚠️ {provider} não encontrado")
                continue
            except Exception as e:
                logger.warning(f"⚠️ Erro com {provider}: {e}")
                continue
        
        logger.warning("⚠️ Nenhum túnel disponível, funcionando apenas localmente")
    
    def health_check_loop(self):
        """Loop de verificação de saúde do sistema"""
        logger.info("🏥 Iniciando monitoramento de saúde...")
        
        failure_count = 0
        interval = self.config["system"]["health_check_interval"]
        threshold = self.config["system"]["restart_threshold"]
        
        while self.is_running:
            try:
                time.sleep(interval)
                
                if not self.is_running:
                    break
                
                # Verificar se servidor ainda está ativo
                if self.server_process and self.server_process.poll() is not None:
                    logger.error("❌ Processo do servidor morreu!")
                    failure_count += 1
                
                # Verificar se servidor responde
                elif not self.test_server_health(self.port):
                    logger.warning("⚠️ Servidor não responde ao health check")
                    failure_count += 1
                
                # Verificar conexão com banco
                elif not self.test_database_connection():
                    logger.warning("⚠️ Problema na conexão com banco de dados")
                    failure_count += 1
                
                else:
                    # Tudo OK
                    if failure_count > 0:
                        logger.info("✅ Sistema recuperado!")
                    failure_count = 0
                    self.last_health_check = datetime.now()
                    continue
                
                # Se chegou aqui, há problemas
                logger.error(f"❌ Health check falhou {failure_count} vez(es)")
                
                if failure_count >= threshold:
                    logger.info("🔄 Limite de falhas atingido, reiniciando sistema...")
                    self.restart_system()
                    failure_count = 0
                    
            except Exception as e:
                logger.error(f"❌ Erro no health check: {e}")
                failure_count += 1
    
    def restart_system(self):
        """Reiniciar todo o sistema"""
        logger.info("🔄 REINICIANDO SISTEMA...")
        self.restart_count += 1
        
        try:
            # Parar processos atuais
            if self.server_process:
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()
                self.server_process = None
            
            if self.tunnel_process:
                self.tunnel_process.terminate()
                self.tunnel_process = None
            
            # Aguardar limpeza
            time.sleep(self.config["recovery"]["recovery_delay"])
            
            # Encontrar nova porta se necessário
            self.port = self.find_available_port()
            
            # Reiniciar servidor
            self.server_process = self.start_web_server(self.port)
            
            if self.server_process:
                # Reiniciar túnel
                self.start_tunnel(self.port)
                
                # Imprimir status
                self.print_status()
                
                logger.info(f"✅ Sistema reiniciado com sucesso! (Tentativa #{self.restart_count})")
            else:
                logger.error("❌ Falha ao reiniciar servidor")
                
        except Exception as e:
            logger.error(f"❌ Erro ao reiniciar sistema: {e}")
            traceback.print_exc()
    
    def print_status(self):
        """Imprimir status atual do sistema"""
        print("\n" + "="*60)
        print("🐘 MAMUTE - SISTEMA DEFINITIVO SEMPRE ONLINE")
        print("="*60)
        print(f"🚀 Status: {'ONLINE' if self.server_process else 'OFFLINE'}")
        print(f"🌐 Porta: {self.port}")
        print(f"🔄 Reinicializações: {self.restart_count}")
        print(f"⏰ Último health check: {self.last_health_check.strftime('%H:%M:%S')}")
        print()
        print("🌐 URLs DISPONÍVEIS:")
        print("-"*40)
        print(f"🏠 Dashboard: http://localhost:{self.port}")
        print(f"💬 Chat:      http://localhost:{self.port}/chat") 
        print(f"📚 API Docs:  http://localhost:{self.port}/docs")
        print("-"*40)
        print("🔄 Sistema monitora-se automaticamente a cada 15s")
        print("🛡️ Reinicialização automática em caso de falhas")
        print("="*60)
    
    def start(self):
        """Iniciar sistema completo"""
        logger.info("🚀 INICIANDO SISTEMA DEFINITIVO MAMUTE...")
        
        try:
            # Verificar dependências
            self.test_database_connection()
            
            # Encontrar porta disponível
            self.port = self.find_available_port()
            
            # Iniciar servidor
            self.server_process = self.start_web_server(self.port)
            
            if not self.server_process:
                logger.error("❌ Falha crítica ao iniciar servidor")
                return False
            
            # Iniciar túnel
            self.start_tunnel(self.port)
            
            # Imprimir status
            self.print_status()
            
            # Abrir navegador
            if self.config["system"]["auto_open_browser"]:
                threading.Timer(3.0, lambda: webbrowser.open(f"http://localhost:{self.port}")).start()
            
            # Iniciar monitoramento em background
            health_thread = threading.Thread(target=self.health_check_loop, daemon=True)
            health_thread.start()
            
            logger.info("✅ Sistema definitivo iniciado com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro crítico ao iniciar sistema: {e}")
            traceback.print_exc()
            return False
    
    def shutdown_handler(self, signum, frame):
        """Handler para shutdown gracioso"""
        logger.info("🛑 Recebido sinal de shutdown...")
        self.shutdown()
    
    def shutdown(self):
        """Shutdown gracioso do sistema"""
        logger.info("🛑 Parando sistema...")
        
        self.is_running = False
        
        if self.server_process:
            logger.info("🔄 Parando servidor web...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
        
        if self.tunnel_process:
            logger.info("🔄 Parando túnel...")
            self.tunnel_process.terminate()
        
        logger.info("✅ Sistema parado com segurança")
        sys.exit(0)
    
    def run_forever(self):
        """Executar sistema indefinidamente"""
        if not self.start():
            logger.error("❌ Falha ao iniciar sistema")
            return
        
        try:
            # Loop principal - mantém sistema ativo
            while self.is_running:
                time.sleep(60)  # Dormir 1 minuto
                
                # Verificação adicional a cada minuto
                if self.server_process and self.server_process.poll() is not None:
                    logger.warning("⚠️ Processo principal morreu, reiniciando...")
                    self.restart_system()
                    
        except KeyboardInterrupt:
            logger.info("🛑 Ctrl+C detectado")
        except Exception as e:
            logger.error(f"❌ Erro no loop principal: {e}")
        finally:
            self.shutdown()


def main():
    """Função principal"""
    print("🐘 MAMUTE - SISTEMA DEFINITIVO SEMPRE ONLINE")
    print("🚀 Iniciando sistema ultra-robusto...")
    
    # Criar e iniciar sistema
    sistema = SistemaDefinitivoMamute()
    sistema.run_forever()


if __name__ == "__main__":
    main()