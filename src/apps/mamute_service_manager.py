#!/usr/bin/env python3
"""
🔄 GERENCIADOR DE SERVIÇO MAMUTE
Mantém a IA rodando 24h automaticamente com recuperação automática
"""

import subprocess
import sys
import os
import time
import json
import signal
import logging
from pathlib import Path
from datetime import datetime
from threading import Thread
import psutil

class MamuteServiceManager:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.log_file = self.project_dir / "logs" / "service.log"
        self.server_log_file = self.project_dir / "logs" / "web_server.log"
        self.pid_file = self.project_dir / "mamute.pid"
        self.config_file = self.project_dir / "service_config.json"
        self.server_log_handle = None
        
        # Criar diretório de logs
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Configurações padrão
        self.config = {
            "auto_restart": True,
            "restart_delay": 10,
            "max_restarts": 10,
            "port": 8001,
            "host": "0.0.0.0",
            "enable_tunneling": True,
            "tunnel_type": "ngrok"  # ngrok, cloudflare, serveo
        }
        
        self.load_config()
        self.current_process = None
        self.restart_count = 0
        self.running = False

    def load_config(self):
        """Carregar configurações do arquivo"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
            else:
                self.save_config()
        except Exception as e:
            self.logger.error(f"Erro ao carregar config: {e}")

    def save_config(self):
        """Salvar configurações"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Erro ao salvar config: {e}")

    def is_port_in_use(self, port):
        """Verificar se a porta está em uso"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port:
                    return True
            return False
        except:
            return False

    def kill_existing_process(self):
        """Matar processo existente se houver"""
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    process.terminate()
                    time.sleep(2)
                    if process.is_running():
                        process.kill()
                    self.logger.info(f"Processo anterior (PID: {pid}) terminado")
                
                self.pid_file.unlink(missing_ok=True)
        except Exception as e:
            self.logger.warning(f"Erro ao terminar processo anterior: {e}")

    def start_tunnel(self):
        """Iniciar túnel se habilitado"""
        if not self.config["enable_tunneling"]:
            return

        tunnel_type = self.config["tunnel_type"]
        
        try:
            if tunnel_type == "ngrok":
                self.logger.info("🚀 Iniciando túnel ngrok...")
                subprocess.Popen(
                    ['ngrok', 'http', str(self.config["port"]), '--log=stdout'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
            elif tunnel_type == "cloudflare":
                self.logger.info("☁️ Iniciando Cloudflare Tunnel...")
                subprocess.Popen(
                    ['cloudflared', 'tunnel', '--url', f'http://localhost:{self.config["port"]}'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
            time.sleep(5)  # Aguardar túnel inicializar
            self.logger.info("✅ Túnel iniciado com sucesso!")
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar túnel: {e}")

    def start_web_server(self):
        """Iniciar servidor web"""
        try:
            # Verificar se porta está livre
            if self.is_port_in_use(self.config["port"]):
                self.logger.warning(f"Porta {self.config['port']} em uso, tentando liberar...")
                self.kill_existing_process()
                time.sleep(3)

            # Comando para iniciar servidor
            cmd = [
                sys.executable,
                "-m", "uvicorn",
                "web_app:app",
                "--host", self.config["host"],
                "--port", str(self.config["port"]),
                "--log-level", "warning"
            ]

            # Iniciar processo
            # Registrar stdout/stderr em arquivo para evitar travamentos por pipe cheio
            self.server_log_handle = open(self.server_log_file, "a", encoding="utf-8")

            self.current_process = subprocess.Popen(
                cmd,
                cwd=self.project_dir,
                stdout=self.server_log_handle,
                stderr=self.server_log_handle,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # Salvar PID
            with open(self.pid_file, 'w') as f:
                f.write(str(self.current_process.pid))

            self.logger.info(f"🚀 Servidor iniciado (PID: {self.current_process.pid})")
            self.logger.info(f"🌐 URL: http://localhost:{self.config['port']}")
            
            return True

        except Exception as e:
            self.logger.error(f"Erro ao iniciar servidor: {e}")
            return False

    def monitor_process(self):
        """Monitorar processo e reiniciar se necessário"""
        while self.running:
            try:
                if self.current_process is None:
                    time.sleep(1)
                    continue

                # Verificar se processo ainda está vivo
                if self.current_process.poll() is not None:
                    self.logger.warning("⚠️ Servidor parou inesperadamente!")
                    
                    # Verificar limite de restart
                    if self.restart_count >= self.config["max_restarts"]:
                        self.logger.error("❌ Limite de restarts atingido. Parando serviço.")
                        self.running = False
                        break
                    
                    if self.config["auto_restart"]:
                        self.restart_count += 1
                        self.logger.info(f"🔄 Reiniciando... (tentativa {self.restart_count})")
                        time.sleep(self.config["restart_delay"])
                        
                        # Reiniciar servidor
                        if self.start_web_server():
                            self.logger.info("✅ Servidor reiniciado com sucesso!")
                        else:
                            self.logger.error("❌ Falha ao reiniciar servidor")
                    else:
                        self.running = False
                        break

                time.sleep(5)  # Verificar a cada 5 segundos

            except Exception as e:
                self.logger.error(f"Erro no monitor: {e}")
                time.sleep(10)

    def start_service(self):
        """Iniciar serviço completo"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("🐘 INICIANDO SERVIÇO MAMUTE 24H")
            self.logger.info("=" * 60)
            
            # Matar processos existentes
            self.kill_existing_process()
            
            # Iniciar servidor
            if not self.start_web_server():
                return False

            # Iniciar túnel
            self.start_tunnel()
            
            # Iniciar monitoramento
            self.running = True
            self.restart_count = 0
            
            monitor_thread = Thread(target=self.monitor_process, daemon=True)
            monitor_thread.start()
            
            self.logger.info("✅ Serviço iniciado! Acesso 24h ativo.")
            self.logger.info(f"📊 Logs em: {self.log_file}")
            
            return True

        except Exception as e:
            self.logger.error(f"Erro ao iniciar serviço: {e}")
            return False

    def stop_service(self):
        """Parar serviço"""
        try:
            self.logger.info("🛑 Parando serviço...")
            self.running = False
            
            if self.current_process:
                self.current_process.terminate()
                time.sleep(3)
                if self.current_process.poll() is None:
                    self.current_process.kill()
            if self.server_log_handle:
                self.server_log_handle.close()
                self.server_log_handle = None
            
            self.kill_existing_process()
            self.logger.info("✅ Serviço parado")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao parar serviço: {e}")
            return False

    def status(self):
        """Verificar status do serviço"""
        try:
            if not self.pid_file.exists():
                return {"running": False, "message": "Serviço não iniciado"}
            
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                uptime = datetime.now() - datetime.fromtimestamp(process.create_time())
                
                return {
                    "running": True,
                    "pid": pid,
                    "uptime": str(uptime).split('.')[0],
                    "restart_count": self.restart_count,
                    "port": self.config["port"]
                }
            else:
                return {"running": False, "message": "Processo não encontrado"}
                
        except Exception as e:
            return {"running": False, "message": f"Erro: {e}"}

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Gerenciador de Serviço Mamute")
    parser.add_argument("command", choices=["start", "stop", "restart", "status", "config"], 
                       help="Comando a executar")
    
    args = parser.parse_args()
    manager = MamuteServiceManager()
    
    if args.command == "start":
        if manager.start_service():
            print("✅ Serviço iniciado com sucesso!")
            try:
                # Manter rodando até Ctrl+C
                while manager.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                manager.stop_service()
        else:
            print("❌ Falha ao iniciar serviço")
            
    elif args.command == "stop":
        if manager.stop_service():
            print("✅ Serviço parado")
        else:
            print("❌ Erro ao parar serviço")
            
    elif args.command == "restart":
        manager.stop_service()
        time.sleep(2)
        if manager.start_service():
            print("✅ Serviço reiniciado")
        else:
            print("❌ Falha ao reiniciar serviço")
            
    elif args.command == "status":
        status = manager.status()
        if status["running"]:
            print(f"✅ Serviço RODANDO")
            print(f"   PID: {status['pid']}")
            print(f"   Uptime: {status['uptime']}")
            print(f"   Porta: {status['port']}")
            print(f"   Restarts: {status['restart_count']}")
        else:
            print(f"❌ Serviço PARADO - {status['message']}")
            
    elif args.command == "config":
        print(f"📋 Configurações em: {manager.config_file}")
        print(json.dumps(manager.config, indent=2))

if __name__ == "__main__":
    main()