#!/usr/bin/env python3
"""
🚀 INICIALIZAÇÃO AUTOMÁTICA - SERVIDORES LOCAL E GLOBAL
Mantém ambos os servidores sempre ativos automaticamente
"""

import subprocess
import time
import logging
import json
import psutil
import signal
import sys
import os
from pathlib import Path
from datetime import datetime
from threading import Thread
import requests

class ServidoresAutomaticos:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.log_dir = self.project_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar logging
        self.log_file = self.log_dir / f"servidores_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Configurações
        self.config = {
            "servidor_local": {
                "porta": 8000,
                "host": "0.0.0.0",
                "arquivo": "web_app.py",
                "ativo": True,
                "auto_restart": True
            },
            "servidor_global": {
                "tunnel_type": "serveo",  # Usar serveo como alternativa ao ngrok
                "porta": 8000,
                "ativo": True,
                "auto_restart": True
            },
            "monitoramento": {
                "intervalo_verificacao": 30,  # segundos
                "max_tentativas_restart": 5,
                "delay_restart": 15
            },
            "urls_publicas": []  # Para armazenar URLs geradas
        }
        
        self.processos = {
            "servidor_local": None,
            "tunnel": None
        }
        
        self.contadores_restart = {
            "servidor_local": 0,
            "tunnel": 0
        }
        
        self.ativo = False
        
    def verificar_porta_livre(self, porta):
        """Verificar se a porta está disponível"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == porta:
                    return False
            return True
        except:
            return True
    
    def matar_processos_na_porta(self, porta):
        """Liberar processos que usam a porta"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.info.get('connections', []):
                        if conn.laddr.port == porta:
                            self.logger.info(f"🔪 Matando processo {proc.info['name']} (PID: {proc.info['pid']}) na porta {porta}")
                            psutil.Process(proc.info['pid']).terminate()
                            time.sleep(2)
                except:
                    pass
        except Exception as e:
            self.logger.warning(f"Erro ao liberar porta {porta}: {e}")
    
    def iniciar_servidor_local(self):
        """Iniciar servidor web local"""
        try:
            porta = self.config["servidor_local"]["porta"]
            
            # Verificar se já está rodando
            if self.processos["servidor_local"] and self.processos["servidor_local"].poll() is None:
                return True
            
            # Liberar porta se necessário
            if not self.verificar_porta_livre(porta):
                self.logger.warning(f"Porta {porta} ocupada, liberando...")
                self.matar_processos_na_porta(porta)
                time.sleep(3)
            
            # Comando para iniciar o servidor
            cmd = [
                sys.executable,
                "-m", "uvicorn",
                "web_app:app",
                "--host", self.config["servidor_local"]["host"],
                "--port", str(porta),
                "--reload",
                "--log-level", "warning"
            ]
            
            # Configurar variáveis de ambiente para o banco
            env = os.environ.copy()
            env["POSTGRES_HOST"] = "localhost"
            env["POSTGRES_PORT"] = "5432"
            env["POSTGRES_DB"] = "ia_database"
            env["POSTGRES_USER"] = "postgres"
            env["POSTGRES_PASSWORD"] = "postgres@"
            env["DATABASE_URL"] = "postgresql://postgres:postgres%40@localhost:5432/ia_database"
            env["AI_NAME"] = "Mamute"
            
            # Iniciar processo
            self.processos["servidor_local"] = subprocess.Popen(
                cmd,
                cwd=self.project_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Aguardar inicialização
            time.sleep(5)
            
            # Verificar se iniciou corretamente
            if self.verificar_servidor_funcionando():
                self.logger.info(f"✅ Servidor local iniciado na porta {porta}")
                self.logger.info(f"🌐 URL Local: http://localhost:{porta}")
                self.logger.info(f"🏠 URL Rede: http://0.0.0.0:{porta}")
                return True
            else:
                self.logger.error("❌ Servidor local falhou ao iniciar")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao iniciar servidor local: {e}")
            return False
    
    def iniciar_tunnel_global(self):
        """Iniciar túnel para acesso global"""
        try:
            tunnel_type = self.config["servidor_global"]["tunnel_type"]
            porta = self.config["servidor_global"]["porta"]
            
            # Verificar se já está rodando
            if self.processos["tunnel"] and self.processos["tunnel"].poll() is None:
                return True
            
            if tunnel_type == "ngrok":
                cmd = ["ngrok", "http", str(porta), "--log=stdout"]
                
            elif tunnel_type == "cloudflare":
                cmd = ["cloudflared", "tunnel", "--url", f"http://localhost:{porta}"]
                
            elif tunnel_type == "serveo":
                cmd = ["ssh", "-R", f"80:localhost:{porta}", "serveo.net"]
                
            else:
                self.logger.error(f"Tipo de túnel desconhecido: {tunnel_type}")
                return False
            
            # Iniciar túnel
            self.processos["tunnel"] = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            time.sleep(8)  # Aguardar túnel conectar
            
            # Verificar se túnel está funcionando
            if self.processos["tunnel"].poll() is None:
                self.logger.info(f"✅ Túnel {tunnel_type} iniciado com sucesso!")
                self.logger.info("🌍 Acesso global ativo!")
                return True
            else:
                self.logger.error(f"❌ Túnel {tunnel_type} falhou ao iniciar")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao iniciar túnel: {e}")
            return False
    
    def verificar_servidor_funcionando(self):
        """Verificar se servidor está respondendo"""
        try:
            response = requests.get(f"http://localhost:{self.config['servidor_local']['porta']}/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def monitorar_processos(self):
        """Monitorar e reiniciar processos se necessário"""
        while self.ativo:
            try:
                # Verificar servidor local
                if self.config["servidor_local"]["ativo"]:
                    if not self.processos["servidor_local"] or self.processos["servidor_local"].poll() is not None:
                        self.logger.warning("⚠️ Servidor local parou!")
                        
                        if self.config["servidor_local"]["auto_restart"]:
                            if self.contadores_restart["servidor_local"] < self.config["monitoramento"]["max_tentativas_restart"]:
                                self.contadores_restart["servidor_local"] += 1
                                self.logger.info(f"🔄 Reiniciando servidor local (tentativa {self.contadores_restart['servidor_local']})")
                                time.sleep(self.config["monitoramento"]["delay_restart"])
                                
                                if self.iniciar_servidor_local():
                                    self.contadores_restart["servidor_local"] = 0
                                    self.logger.info("✅ Servidor local reiniciado!")
                            else:
                                self.logger.error("❌ Limite de tentativas de restart do servidor local atingido")
                
                # Verificar túnel global
                if self.config["servidor_global"]["ativo"]:
                    if not self.processos["tunnel"] or self.processos["tunnel"].poll() is not None:
                        self.logger.warning("⚠️ Túnel global parou!")
                        
                        if self.config["servidor_global"]["auto_restart"]:
                            if self.contadores_restart["tunnel"] < self.config["monitoramento"]["max_tentativas_restart"]:
                                self.contadores_restart["tunnel"] += 1
                                self.logger.info(f"🔄 Reiniciando túnel global (tentativa {self.contadores_restart['tunnel']})")
                                time.sleep(self.config["monitoramento"]["delay_restart"])
                                
                                if self.iniciar_tunnel_global():
                                    self.contadores_restart["tunnel"] = 0
                                    self.logger.info("✅ Túnel global reiniciado!")
                            else:
                                self.logger.error("❌ Limite de tentativas de restart do túnel atingido")
                
                # Aguardar antes da próxima verificação
                time.sleep(self.config["monitoramento"]["intervalo_verificacao"])
                
            except Exception as e:
                self.logger.error(f"Erro no monitoramento: {e}")
                time.sleep(30)
    
    def status_completo(self):
        """Mostrar status completo dos servidores"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "servidor_local": {
                "ativo": False,
                "processo": None,
                "url": f"http://localhost:{self.config['servidor_local']['porta']}"
            },
            "servidor_global": {
                "ativo": False,
                "processo": None,
                "tipo": self.config["servidor_global"]["tunnel_type"]
            }
        }
        
        # Verificar servidor local
        if self.processos["servidor_local"] and self.processos["servidor_local"].poll() is None:
            status["servidor_local"]["ativo"] = True
            status["servidor_local"]["processo"] = self.processos["servidor_local"].pid
        
        # Verificar túnel
        if self.processos["tunnel"] and self.processos["tunnel"].poll() is None:
            status["servidor_global"]["ativo"] = True
            status["servidor_global"]["processo"] = self.processos["tunnel"].pid
        
        return status
    
    def parar_tudo(self):
        """Parar todos os serviços"""
        self.logger.info("🛑 Parando todos os serviços...")
        self.ativo = False
        
        # Parar processos
        for nome, processo in self.processos.items():
            if processo and processo.poll() is None:
                try:
                    processo.terminate()
                    time.sleep(3)
                    if processo.poll() is None:
                        processo.kill()
                    self.logger.info(f"✅ {nome} parado")
                except Exception as e:
                    self.logger.error(f"Erro ao parar {nome}: {e}")
        
        self.logger.info("✅ Todos os serviços foram parados")
    
    def iniciar_tudo(self):
        """Iniciar todos os serviços automaticamente"""
        self.logger.info("=" * 70)
        self.logger.info("🚀 INICIANDO SERVIDORES AUTOMÁTICOS - LOCAL E GLOBAL")
        self.logger.info("=" * 70)
        
        self.ativo = True
        
        # Iniciar servidor local
        if self.config["servidor_local"]["ativo"]:
            self.logger.info("🏠 Iniciando servidor local...")
            self.iniciar_servidor_local()
        
        # Iniciar túnel global
        if self.config["servidor_global"]["ativo"]:
            self.logger.info("🌍 Iniciando acesso global...")
            self.iniciar_tunnel_global()
        
        # Iniciar monitoramento
        monitor_thread = Thread(target=self.monitorar_processos, daemon=True)
        monitor_thread.start()
        
        self.logger.info("=" * 70)
        self.logger.info("✅ AMBOS OS SERVIDORES ATIVOS E MONITORADOS!")
        self.logger.info("🔄 Recuperação automática habilitada")
        self.logger.info("📊 Verificação a cada 30 segundos")
        self.logger.info("=" * 70)
        
        # Mostrar status
        status = self.status_completo()
        self.logger.info(f"🏠 Servidor Local: {'✅ ATIVO' if status['servidor_local']['ativo'] else '❌ INATIVO'}")
        self.logger.info(f"🌍 Servidor Global: {'✅ ATIVO' if status['servidor_global']['ativo'] else '❌ INATIVO'}")
        
        return True

def main():
    servidores = ServidoresAutomaticos()
    
    try:
        # Configurar handler para Ctrl+C
        def signal_handler(signum, frame):
            servidores.parar_tudo()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Iniciar tudo
        servidores.iniciar_tudo()
        
        # Manter rodando
        while servidores.ativo:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
        
    except KeyboardInterrupt:
        servidores.parar_tudo()
    except Exception as e:
        logging.error(f"Erro fatal: {e}")
        servidores.parar_tudo()

if __name__ == "__main__":
    main()