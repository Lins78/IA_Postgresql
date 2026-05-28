#!/usr/bin/env python3
"""
🚀 SISTEMA DE SERVIDORES AUTOMÁTICOS MAMUTE 
Mantém servidor local sempre ativo + opções de túnel global
"""

import subprocess
import time
import logging
import psutil
import signal
import sys
import os
import requests
from pathlib import Path
from datetime import datetime
from threading import Thread
import webbrowser

class MamuteServidoresAuto:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.log_dir = self.project_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar logging
        self.log_file = self.log_dir / f"servidor_auto_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.config = {
            "servidor_local": {
                "porta": 8002,
                "host": "0.0.0.0",
                "ativo": True,
                "auto_restart": True,
                "abrir_navegador": True
            },
            "monitoramento": {
                "intervalo_verificacao": 30,
                "max_tentativas_restart": 5,
                "delay_restart": 10
            }
        }
        
        self.processo_servidor = None
        self.contador_restart = 0
        self.ativo = False
        self.urls_disponiveis = []
        
    def limpar_porta(self, porta):
        """Liberar processos na porta"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.info.get('connections', []):
                        if hasattr(conn.laddr, 'port') and conn.laddr.port == porta:
                            self.logger.info(f"🔄 Liberando processo {proc.info['name']} (PID: {proc.info['pid']}) da porta {porta}")
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
            host = self.config["servidor_local"]["host"]
            
            # Verificar se já está rodando
            if self.processo_servidor and self.processo_servidor.poll() is None:
                return True
            
            # Liberar porta se necessário
            self.limpar_porta(porta)
            
            # Configurar ambiente
            env = os.environ.copy()
            env.update({
                "POSTGRES_HOST": "localhost",
                "POSTGRES_PORT": "5432", 
                "POSTGRES_DB": "ia_database",
                "POSTGRES_USER": "postgres",
                "POSTGRES_PASSWORD": "postgres@",
                "DATABASE_URL": "postgresql://postgres:postgres%40@localhost:5432/ia_database",
                "AI_NAME": "Mamute",
                "PYTHONPATH": str(self.project_dir)
            })
            
            # Comando para iniciar servidor
            cmd = [
                sys.executable, "-m", "uvicorn",
                "web_app:app",
                "--host", host,
                "--port", str(porta),
                "--reload"
            ]
            
            self.logger.info(f"🚀 Iniciando servidor Mamute em {host}:{porta}...")
            
            # Iniciar processo
            self.processo_servidor = subprocess.Popen(
                cmd,
                cwd=self.project_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Aguardar inicialização
            self.logger.info("⏳ Aguardando inicialização do servidor...")
            time.sleep(8)
            
            # Verificar se está funcionando
            if self.verificar_servidor_ativo():
                self.logger.info("✅ Servidor Mamute iniciado com sucesso!")
                self.urls_disponiveis = [
                    f"http://localhost:{porta}",
                    f"http://127.0.0.1:{porta}",
                    f"http://0.0.0.0:{porta}"
                ]
                
                # Mostrar URLs
                self.mostrar_urls()
                
                # Abrir navegador se configurado
                if self.config["servidor_local"]["abrir_navegador"]:
                    self.abrir_navegador()
                
                return True
            else:
                self.logger.error("❌ Servidor falhou ao inicializar")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao iniciar servidor: {e}")
            return False

    def verificar_servidor_ativo(self):
        """Verificar se servidor está respondendo"""
        porta = self.config["servidor_local"]["porta"]
        try:
            response = requests.get(f"http://localhost:{porta}/health", timeout=10)
            return response.status_code == 200
        except:
            try:
                # Tentar endpoint principal se /health não existir
                response = requests.get(f"http://localhost:{porta}/", timeout=10)
                return response.status_code == 200
            except:
                return False

    def mostrar_urls(self):
        """Mostrar URLs disponíveis"""
        porta = self.config["servidor_local"]["porta"]
        self.logger.info("🌐 SERVIDOR MAMUTE ATIVO - URLs DISPONÍVEIS:")
        self.logger.info("=" * 60)
        self.logger.info(f"🏠 Dashboard Principal: http://localhost:{porta}")
        self.logger.info(f"💬 Chat Interativo:    http://localhost:{porta}/chat")
        self.logger.info(f"📚 API Documentação:   http://localhost:{porta}/docs")
        self.logger.info(f"📊 Métricas Sistema:   http://localhost:{porta}/api/metrics")
        self.logger.info("=" * 60)

    def abrir_navegador(self):
        """Abrir navegador automaticamente"""
        try:
            porta = self.config["servidor_local"]["porta"]
            url = f"http://localhost:{porta}"
            self.logger.info(f"🌐 Abrindo navegador em {url}")
            webbrowser.open(url)
        except Exception as e:
            self.logger.warning(f"Não foi possível abrir navegador: {e}")

    def monitorar_servidor(self):
        """Monitorar servidor e reiniciar se necessário"""
        while self.ativo:
            try:
                time.sleep(self.config["monitoramento"]["intervalo_verificacao"])
                
                # Verificar se processo ainda está rodando
                if not self.processo_servidor or self.processo_servidor.poll() is not None:
                    self.logger.warning("⚠️ Servidor parou! Tentando reiniciar...")
                    
                    if self.contador_restart < self.config["monitoramento"]["max_tentativas_restart"]:
                        self.contador_restart += 1
                        self.logger.info(f"🔄 Tentativa de restart {self.contador_restart}/{self.config['monitoramento']['max_tentativas_restart']}")
                        
                        time.sleep(self.config["monitoramento"]["delay_restart"])
                        
                        if self.iniciar_servidor_local():
                            self.contador_restart = 0
                            self.logger.info("✅ Servidor reiniciado com sucesso!")
                        else:
                            self.logger.error("❌ Falha ao reiniciar servidor")
                    else:
                        self.logger.error("❌ Limite de tentativas de restart atingido")
                        self.parar()
                        break
                
                # Verificar se está respondendo
                elif not self.verificar_servidor_ativo():
                    self.logger.warning("⚠️ Servidor não está respondendo")
                    
                else:
                    # Servidor OK
                    if self.contador_restart > 0:
                        self.logger.info("✅ Servidor estável novamente")
                        self.contador_restart = 0
                        
            except Exception as e:
                self.logger.error(f"Erro no monitoramento: {e}")
                time.sleep(5)

    def iniciar(self):
        """Iniciar sistema completo"""
        self.logger.info("🐘 INICIANDO SISTEMA MAMUTE AUTOMÁTICO")
        self.logger.info("=" * 70)
        
        # Verificar se PostgreSQL está rodando
        self.verificar_postgresql()
        
        # Iniciar servidor local
        if not self.iniciar_servidor_local():
            self.logger.error("❌ Falha ao iniciar servidor local")
            return False
        
        # Ativar monitoramento
        self.ativo = True
        
        # Iniciar thread de monitoramento
        monitor_thread = Thread(target=self.monitorar_servidor, daemon=True)
        monitor_thread.start()
        
        self.logger.info("🎯 Sistema automático ativado!")
        self.logger.info("🔄 Monitoramento contínuo iniciado")
        self.logger.info("⚡ Auto-restart configurado")
        
        return True

    def verificar_postgresql(self):
        """Verificar se PostgreSQL está disponível"""
        try:
            import psycopg2
            conn = psycopg2.connect(
                host="localhost",
                port="5432",
                user="postgres",
                password="postgres@",
                database="ia_database"
            )
            conn.close()
            self.logger.info("✅ PostgreSQL conectado e disponível")
        except Exception as e:
            self.logger.warning(f"⚠️ PostgreSQL: {e}")

    def mostrar_opcoes_tunnel(self):
        """Mostrar opções de túnel global"""
        porta = self.config["servidor_local"]["porta"]
        self.logger.info("\n🌍 OPÇÕES PARA ACESSO GLOBAL:")
        self.logger.info("-" * 50)
        self.logger.info("1. 📡 NGROK (Recomendado):")
        self.logger.info("   • Baixe: https://ngrok.com/download")
        self.logger.info(f"   • Execute: ngrok http {porta}")
        self.logger.info("")
        self.logger.info("2. 🔗 SERVEO (SSH):")
        self.logger.info(f"   • Execute: ssh -R 80:localhost:{porta} serveo.net")
        self.logger.info("")
        self.logger.info("3. ☁️ CLOUDFLARE TUNNEL:")
        self.logger.info("   • Instale cloudflared")
        self.logger.info(f"   • Execute: cloudflared tunnel --url http://localhost:{porta}")

    def parar(self):
        """Parar sistema"""
        self.logger.info("🛑 Parando sistema Mamute...")
        self.ativo = False
        
        if self.processo_servidor and self.processo_servidor.poll() is None:
            self.processo_servidor.terminate()
            self.processo_servidor.wait()
        
        self.logger.info("✅ Sistema parado com sucesso")

    def executar(self):
        """Execução principal"""
        try:
            if self.iniciar():
                # Mostrar opções de túnel
                self.mostrar_opcoes_tunnel()
                
                self.logger.info("\n" + "=" * 70)
                self.logger.info("🚀 MAMUTE RODANDO AUTOMATICAMENTE!")
                self.logger.info("=" * 70)
                self.logger.info("🔄 Sistema manterá servidor ativo automaticamente")
                self.logger.info("🛑 Para parar: Pressione Ctrl+C")
                self.logger.info("=" * 70)
                
                # Manter rodando
                while self.ativo:
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            self.logger.info("\n🛑 Interrupção solicitada pelo usuário")
        except Exception as e:
            self.logger.error(f"❌ Erro inesperado: {e}")
        finally:
            self.parar()

def main():
    sistema = MamuteServidoresAuto()
    sistema.executar()

if __name__ == "__main__":
    main()