#!/usr/bin/env python3
"""
🚀 SISTEMA DE CONEXÃO DEFINITIVO - MAMUTE SEMPRE ONLINE
Sistema robusto que garante conexão local e global 24/7
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
from datetime import datetime
from pathlib import Path
import uvicorn
from typing import Optional, Dict, Any
import asyncio
import signal

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mamute_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MamuteConnectionManager:
    """Gerenciador de conexão definitivo do Mamute"""
    
    def __init__(self):
        self.local_port = 8000
        self.local_process = None
        self.tunnel_process = None
        self.tunnel_url = None
        self.is_running = True
        self.health_check_interval = 30  # 30 segundos
        self.restart_attempts = 0
        self.max_restart_attempts = 5
        self.config_file = Path("mamute_config.json")
        
        # Configurações do sistema
        self.config = self.load_or_create_config()
        
    def load_or_create_config(self) -> Dict[str, Any]:
        """Carregar ou criar configuração do sistema"""
        default_config = {
            "postgres": {
                "host": "localhost",
                "port": "5432",
                "user": "postgres",
                "password": "postgres@",
                "database": "ia_database"
            },
            "server": {
                "port": 8000,
                "host": "0.0.0.0"
            },
            "tunnels": {
                "preferred": "ngrok",  # ngrok, cloudflare, serveo
                "fallback": ["cloudflare", "serveo"]
            },
            "monitoring": {
                "health_check_interval": 30,
                "max_restart_attempts": 5,
                "auto_recovery": True
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Merge com defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                logger.error(f"Erro ao carregar config: {e}")
                
        # Criar config padrão
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        return default_config
    
    def setup_environment(self):
        """Configurar variáveis de ambiente"""
        pg_config = self.config["postgres"]
        
        env_vars = {
            "POSTGRES_HOST": pg_config["host"],
            "POSTGRES_PORT": pg_config["port"],
            "POSTGRES_DB": pg_config["database"],
            "POSTGRES_USER": pg_config["user"],
            "POSTGRES_PASSWORD": pg_config["password"],
            "DATABASE_URL": f"postgresql://{pg_config['user']}:{pg_config['password']}@{pg_config['host']}:{pg_config['port']}/{pg_config['database']}",
            "AI_NAME": "Mamute",
            "ENVIRONMENT": "production"
        }
        
        os.environ.update(env_vars)
        
    def is_port_free(self, port: int) -> bool:
        """Verificar se porta está livre"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return False
        return True
    
    def kill_process_on_port(self, port: int):
        """Matar processo usando a porta"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.connections():
                        if conn.laddr.port == port:
                            proc.terminate()
                            proc.wait(timeout=3)
                            logger.info(f"Processo {proc.info['name']} (PID: {proc.info['pid']}) terminado da porta {port}")
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.error(f"Erro ao matar processo na porta {port}: {e}")
        return False
    
    def test_database_connection(self) -> bool:
        """Testar conexão com PostgreSQL"""
        try:
            import psycopg2
            pg_config = self.config["postgres"]
            
            conn = psycopg2.connect(
                host=pg_config["host"],
                port=pg_config["port"],
                user=pg_config["user"],
                password=pg_config["password"],
                database="postgres"  # Testar com banco padrão primeiro
            )
            conn.close()
            logger.info("✅ Conexão PostgreSQL: OK")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na conexão PostgreSQL: {e}")
            return False
    
    def start_local_server(self) -> Optional[subprocess.Popen]:
        """Iniciar servidor local com robustez"""
        
        # Verificar e limpar porta
        if not self.is_port_free(self.local_port):
            logger.info(f"Porta {self.local_port} ocupada, liberando...")
            self.kill_process_on_port(self.local_port)
            time.sleep(2)
        
        # Configurar ambiente
        self.setup_environment()
        
        # Comando para iniciar servidor
        cmd = [
            sys.executable, "-m", "uvicorn",
            "mamute_completo:app",  # Usar arquivo principal
            "--host", self.config["server"]["host"],
            "--port", str(self.config["server"]["port"]),
            "--workers", "1",
            "--access-log"
        ]
        
        try:
            logger.info("🚀 Iniciando servidor local Mamute...")
            
            # Iniciar processo
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            
            # Aguardar inicialização
            for attempt in range(30):  # 30 segundos timeout
                time.sleep(1)
                
                if process.poll() is not None:
                    # Processo morreu
                    stdout, stderr = process.communicate()
                    logger.error(f"Servidor falhou ao iniciar:\nSTDOUT: {stdout}\nSTDERR: {stderr}")
                    return None
                
                # Testar se está respondendo
                try:
                    response = requests.get(f"http://localhost:{self.local_port}/", timeout=2)
                    if response.status_code == 200:
                        logger.info(f"✅ Servidor local ativo: http://localhost:{self.local_port}")
                        return process
                except:
                    continue
                    
            # Timeout
            process.terminate()
            logger.error("❌ Timeout na inicialização do servidor")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar servidor: {e}")
            return None
    
    def start_ngrok_tunnel(self) -> Optional[subprocess.Popen]:
        """Iniciar túnel ngrok"""
        try:
            cmd = ["ngrok", "http", str(self.local_port)]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Aguardar túnel conectar
            time.sleep(5)
            
            # Obter URL do túnel
            try:
                response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
                if response.status_code == 200:
                    tunnels = response.json().get("tunnels", [])
                    if tunnels:
                        self.tunnel_url = tunnels[0]["public_url"]
                        logger.info(f"✅ Túnel ngrok ativo: {self.tunnel_url}")
                        return process
            except Exception as e:
                logger.error(f"Erro ao obter URL do túnel: {e}")
                
            return process
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar túnel ngrok: {e}")
            return None
    
    def start_cloudflare_tunnel(self) -> Optional[subprocess.Popen]:
        """Iniciar túnel Cloudflare como fallback"""
        try:
            # Verificar se cloudflared existe
            cloudflared_path = "cloudflared.exe"
            if not os.path.exists(cloudflared_path):
                logger.info("📥 Baixando Cloudflare Tunnel...")
                import urllib.request
                url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
                urllib.request.urlretrieve(url, cloudflared_path)
                logger.info("✅ Cloudflare Tunnel baixado")
            
            cmd = [cloudflared_path, "tunnel", "--url", f"http://localhost:{self.local_port}"]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(5)
            logger.info("✅ Túnel Cloudflare ativo")
            return process
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar túnel Cloudflare: {e}")
            return None
    
    def start_serveo_tunnel(self) -> Optional[subprocess.Popen]:
        """Iniciar túnel Serveo como último recurso"""
        try:
            cmd = ["ssh", "-R", f"80:localhost:{self.local_port}", "serveo.net"]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            time.sleep(5)
            logger.info("✅ Túnel Serveo ativo")
            return process
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar túnel Serveo: {e}")
            return None
    
    def start_tunnel(self) -> Optional[subprocess.Popen]:
        """Iniciar túnel com fallbacks"""
        tunnels = {
            "ngrok": self.start_ngrok_tunnel,
            "cloudflare": self.start_cloudflare_tunnel,
            "serveo": self.start_serveo_tunnel
        }
        
        # Tentar túnel preferido
        preferred = self.config["tunnels"]["preferred"]
        if preferred in tunnels:
            logger.info(f"🌍 Tentando túnel preferido: {preferred}")
            process = tunnels[preferred]()
            if process:
                return process
        
        # Tentar fallbacks
        for fallback in self.config["tunnels"]["fallback"]:
            if fallback in tunnels:
                logger.info(f"🔄 Tentando fallback: {fallback}")
                process = tunnels[fallback]()
                if process:
                    return process
        
        logger.error("❌ Nenhum túnel pôde ser iniciado")
        return None
    
    def health_check(self) -> bool:
        """Verificar saúde do sistema"""
        try:
            # Verificar servidor local
            response = requests.get(f"http://localhost:{self.local_port}/", timeout=5)
            if response.status_code != 200:
                return False
            
            # Verificar processo local
            if self.local_process and self.local_process.poll() is not None:
                return False
            
            # Verificar processo túnel
            if self.tunnel_process and self.tunnel_process.poll() is not None:
                logger.warning("⚠️ Túnel desconectado, tentando reconectar...")
                self.tunnel_process = self.start_tunnel()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Health check falhou: {e}")
            return False
    
    def restart_system(self):
        """Reiniciar sistema completo"""
        logger.info("🔄 Reiniciando sistema...")
        
        # Parar processos existentes
        if self.local_process:
            self.local_process.terminate()
            self.local_process = None
            
        if self.tunnel_process:
            self.tunnel_process.terminate()
            self.tunnel_process = None
        
        # Aguardar um pouco
        time.sleep(5)
        
        # Reiniciar
        return self.start_system()
    
    def start_system(self) -> bool:
        """Iniciar sistema completo"""
        logger.info("🚀 INICIANDO SISTEMA MAMUTE DEFINITIVO")
        logger.info("=" * 50)
        
        # 1. Verificar banco
        if not self.test_database_connection():
            logger.error("❌ PostgreSQL não conectou - verifique configurações")
            return False
        
        # 2. Iniciar servidor local
        self.local_process = self.start_local_server()
        if not self.local_process:
            logger.error("❌ Falha ao iniciar servidor local")
            return False
        
        # 3. Iniciar túnel
        self.tunnel_process = self.start_tunnel()
        if not self.tunnel_process:
            logger.warning("⚠️ Túnel não iniciou - apenas acesso local disponível")
        
        logger.info("✅ SISTEMA MAMUTE ONLINE!")
        logger.info("=" * 50)
        logger.info(f"🏠 Local:  http://localhost:{self.local_port}")
        if self.tunnel_url:
            logger.info(f"🌍 Global: {self.tunnel_url}")
        logger.info("💬 Chat:  /chat")
        logger.info("📚 Docs:  /docs")
        logger.info("=" * 50)
        
        return True
    
    def monitor_system(self):
        """Monitor contínuo do sistema"""
        logger.info("📊 Iniciando monitor de sistema...")
        
        while self.is_running:
            try:
                time.sleep(self.health_check_interval)
                
                if not self.health_check():
                    logger.warning("⚠️ Sistema com problemas, tentando recovery...")
                    self.restart_attempts += 1
                    
                    if self.restart_attempts <= self.max_restart_attempts:
                        if self.restart_system():
                            self.restart_attempts = 0
                            logger.info("✅ Recovery bem-sucedido")
                        else:
                            logger.error(f"❌ Falha no recovery (tentativa {self.restart_attempts})")
                    else:
                        logger.error("❌ Máximo de tentativas de restart atingido")
                        break
                else:
                    # Reset contador se tudo estiver OK
                    self.restart_attempts = 0
                    logger.info("✅ Sistema saudável")
                    
            except KeyboardInterrupt:
                logger.info("🛑 Parando monitor...")
                break
            except Exception as e:
                logger.error(f"❌ Erro no monitor: {e}")
    
    def stop_system(self):
        """Parar sistema completo"""
        logger.info("🛑 Parando sistema...")
        
        self.is_running = False
        
        if self.local_process:
            self.local_process.terminate()
            logger.info("✅ Servidor local parado")
        
        if self.tunnel_process:
            self.tunnel_process.terminate()
            logger.info("✅ Túnel parado")
    
    def run_forever(self):
        """Executar sistema indefinidamente"""
        
        def signal_handler(signum, frame):
            logger.info("🛑 Sinal de parada recebido")
            self.stop_system()
            sys.exit(0)
        
        # Registrar handlers de sinal
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Iniciar sistema
            if self.start_system():
                # Iniciar monitor em thread separada
                monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
                monitor_thread.start()
                
                # Manter processo principal vivo
                logger.info("🔄 Sistema rodando... (Ctrl+C para parar)")
                while self.is_running:
                    time.sleep(1)
            else:
                logger.error("❌ Falha ao iniciar sistema")
                return False
                
        except KeyboardInterrupt:
            logger.info("🛑 Parando por solicitação do usuário")
        finally:
            self.stop_system()
        
        return True


def main():
    """Função principal"""
    print("🐘 MAMUTE - SISTEMA DE CONEXÃO DEFINITIVO")
    print("=========================================")
    print("✅ Conexão local robusta")
    print("✅ Múltiplos túneis globais")
    print("✅ Recovery automático")
    print("✅ Monitor 24/7")
    print("=========================================")
    print()
    
    manager = MamuteConnectionManager()
    
    try:
        manager.run_forever()
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()