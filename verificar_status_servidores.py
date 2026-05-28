#!/usr/bin/env python3
"""
📊 VERIFICADOR DE STATUS - SERVIDORES IA MAMUTE
Mostra status em tempo real dos servidores local e global
"""

import psutil
import requests
import json
import time
import os
from datetime import datetime
from pathlib import Path

class StatusChecker:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        
    def verificar_porta_ativa(self, porta):
        """Verificar se a porta está sendo usada e por qual processo"""
        processos_na_porta = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    for conn in proc.info.get('connections', []):
                        if hasattr(conn, 'laddr') and conn.laddr.port == porta:
                            processos_na_porta.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'porta': porta
                            })
                except:
                    pass
        except:
            pass
        return processos_na_porta
    
    def testar_conexao_servidor(self, url, timeout=5):
        """Testar se servidor está respondendo"""
        try:
            response = requests.get(url, timeout=timeout)
            return {
                'ativo': True,
                'status_code': response.status_code,
                'tempo_resposta': response.elapsed.total_seconds()
            }
        except requests.exceptions.RequestException as e:
            return {
                'ativo': False,
                'erro': str(e)
            }
    
    def verificar_tunnels_ativos(self):
        """Verificar se há túneis rodando"""
        tunnels = []
        
        # Verificar ngrok
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'ngrok' in proc.info['name'].lower():
                    tunnels.append({
                        'tipo': 'ngrok',
                        'pid': proc.info['pid'],
                        'comando': ' '.join(proc.info['cmdline'])
                    })
            except:
                pass
        
        # Verificar cloudflare
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'cloudflared' in proc.info['name'].lower():
                    tunnels.append({
                        'tipo': 'cloudflare',
                        'pid': proc.info['pid'],
                        'comando': ' '.join(proc.info['cmdline'])
                    })
            except:
                pass
        
        return tunnels
    
    def verificar_servidores_python(self):
        """Verificar servidores Python em execução"""
        servidores = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline']).lower()
                if ('python' in proc.info['name'].lower() and 
                    ('uvicorn' in cmdline or 'fastapi' in cmdline or 'web_app' in cmdline)):
                    servidores.append({
                        'pid': proc.info['pid'],
                        'nome': proc.info['name'],
                        'comando': ' '.join(proc.info['cmdline'])
                    })
            except:
                pass
        
        return servidores
    
    def obter_status_completo(self):
        """Obter status completo de todos os serviços"""
        status = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'servidor_local': {
                'porta_8000': self.verificar_porta_ativa(8000),
                'teste_http': self.testar_conexao_servidor('http://localhost:8000'),
                'servidores_python': self.verificar_servidores_python()
            },
            'acesso_global': {
                'tunnels_ativos': self.verificar_tunnels_ativos()
            },
            'sistema': {
                'uso_cpu': psutil.cpu_percent(interval=1),
                'uso_memoria': psutil.virtual_memory().percent,
                'uptime': datetime.now() - datetime.fromtimestamp(psutil.boot_time())
            }
        }
        
        return status
    
    def imprimir_status_formatado(self, status):
        """Imprimir status de forma organizada"""
        print("=" * 80)
        print(f"📊 STATUS DOS SERVIDORES - {status['timestamp']}")
        print("=" * 80)
        
        # Servidor Local
        print("🏠 SERVIDOR LOCAL:")
        if status['servidor_local']['porta_8000']:
            for proc in status['servidor_local']['porta_8000']:
                print(f"   ✅ Porta 8000 ativa - PID: {proc['pid']} ({proc['name']})")
        else:
            print("   ❌ Porta 8000 não está sendo usada")
        
        http_status = status['servidor_local']['teste_http']
        if http_status['ativo']:
            print(f"   ✅ HTTP respondendo - Status: {http_status['status_code']} - Tempo: {http_status['tempo_resposta']:.3f}s")
        else:
            print(f"   ❌ HTTP não responde - {http_status.get('erro', 'Erro desconhecido')}")
        
        if status['servidor_local']['servidores_python']:
            print("   🐍 Servidores Python ativos:")
            for srv in status['servidor_local']['servidores_python']:
                print(f"      - PID {srv['pid']}: {srv['nome']}")
        
        print()
        
        # Acesso Global
        print("🌍 ACESSO GLOBAL:")
        tunnels = status['acesso_global']['tunnels_ativos']
        if tunnels:
            for tunnel in tunnels:
                print(f"   ✅ Túnel {tunnel['tipo']} ativo - PID: {tunnel['pid']}")
        else:
            print("   ❌ Nenhum túnel ativo encontrado")
        
        print()
        
        # Sistema
        print("💻 SISTEMA:")
        print(f"   CPU: {status['sistema']['uso_cpu']:.1f}%")
        print(f"   RAM: {status['sistema']['uso_memoria']:.1f}%")
        print(f"   Uptime: {str(status['sistema']['uptime']).split('.')[0]}")
        
        print("=" * 80)
    
    def monitorar_continuo(self, intervalo=10):
        """Monitorar status continuamente"""
        print("🔄 Monitoramento contínuo iniciado (Ctrl+C para parar)")
        print(f"📊 Atualizando a cada {intervalo} segundos")
        print()
        
        try:
            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                status = self.obter_status_completo()
                self.imprimir_status_formatado(status)
                
                print(f"\n⏱️ Próxima atualização em {intervalo}s... (Ctrl+C para parar)")
                time.sleep(intervalo)
                
        except KeyboardInterrupt:
            print("\n✅ Monitoramento parado")

def main():
    checker = StatusChecker()
    
    print("📊 VERIFICADOR DE STATUS - SERVIDORES IA MAMUTE")
    print()
    print("Escolha uma opção:")
    print("1. ⚡ Status rápido")
    print("2. 📋 Status detalhado")  
    print("3. 🔄 Monitoramento contínuo")
    print("4. 💾 Salvar relatório")
    print()
    
    try:
        opcao = input("Digite sua escolha (1-4): ").strip()
        
        if opcao == "1":
            print("\n⚡ Status rápido:")
            status = checker.obter_status_completo()
            
            # Status resumido
            local_ok = bool(status['servidor_local']['teste_http']['ativo'])
            global_ok = bool(status['acesso_global']['tunnels_ativos'])
            
            print(f"🏠 Servidor Local:  {'✅ ATIVO' if local_ok else '❌ INATIVO'}")
            print(f"🌍 Acesso Global:   {'✅ ATIVO' if global_ok else '❌ INATIVO'}")
            print(f"📊 URL: http://localhost:8000")
            
        elif opcao == "2":
            status = checker.obter_status_completo()
            checker.imprimir_status_formatado(status)
            
        elif opcao == "3":
            intervalo = input("Intervalo de atualização em segundos (padrão: 10): ").strip()
            try:
                intervalo = int(intervalo) if intervalo else 10
            except ValueError:
                intervalo = 10
            checker.monitorar_continuo(intervalo)
            
        elif opcao == "4":
            status = checker.obter_status_completo()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            arquivo = checker.project_dir / f"relatorio_status_{timestamp}.json"
            
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"💾 Relatório salvo em: {arquivo}")
            checker.imprimir_status_formatado(status)
            
        else:
            print("❌ Opção inválida")
            
    except KeyboardInterrupt:
        print("\n✅ Operação cancelada")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()