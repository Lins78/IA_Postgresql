#!/usr/bin/env python3
"""
🚀 INICIADOR SIMPLES E ROBUSTO - MAMUTE
Sistema que mantém servidor sempre ativo
"""

import subprocess
import time
import requests
import os
import sys
import webbrowser
from pathlib import Path

def verificar_porta_livre(porta):
    """Verificar se porta está disponível"""
    try:
        response = requests.get(f"http://localhost:{porta}", timeout=2)
        return False  # Porta ocupada
    except:
        return True  # Porta livre

def iniciar_servidor():
    """Iniciar servidor Mamute"""
    print("🐘 INICIANDO SERVIDOR MAMUTE")
    print("=" * 50)
    
    porta = 8000
    
    # Configurar ambiente
    env = os.environ.copy()
    env.update({
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "ia_database", 
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "postgres@",
        "DATABASE_URL": "postgresql://postgres:postgres%40@localhost:5432/ia_database",
        "AI_NAME": "Mamute"
    })
    
    # Comando
    cmd = [
        sys.executable, "-m", "uvicorn",
        "web_app:app",
        "--host", "0.0.0.0",
        "--port", str(porta),
        "--reload"
    ]
    
    try:
        print(f"🚀 Iniciando em http://0.0.0.0:{porta}...")
        
        # Iniciar processo
        processo = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Aguardar inicialização
        print("⏳ Aguardando servidor inicializar...")
        
        # Monitorar saída em tempo real
        inicializado = False
        timeout_count = 0
        
        while timeout_count < 30:  # 30 segundos timeout
            time.sleep(1)
            timeout_count += 1
            
            # Verificar se processo ainda está rodando
            if processo.poll() is not None:
                print("❌ Processo terminou inesperadamente")
                return None
                
            # Testar se servidor está respondendo
            try:
                response = requests.get(f"http://localhost:{porta}", timeout=2)
                if response.status_code == 200:
                    inicializado = True
                    break
            except:
                continue
        
        if inicializado:
            print("✅ Servidor Mamute iniciado com sucesso!")
            print()
            print("🌐 URLs DISPONÍVEIS:")
            print("=" * 40)
            print(f"🏠 Dashboard:    http://localhost:{porta}")
            print(f"💬 Chat:         http://localhost:{porta}/chat")
            print(f"📚 API Docs:     http://localhost:{porta}/docs")
            print("=" * 40)
            
            # Abrir navegador
            try:
                print("🌐 Abrindo navegador...")
                webbrowser.open(f"http://localhost:{porta}")
            except:
                print("⚠️ Não foi possível abrir navegador automaticamente")
            
            return processo
        else:
            print("❌ Timeout: Servidor não respondeu em 30 segundos")
            processo.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return None

def monitorar_servidor(processo, intervalo=30):
    """Monitorar servidor e manter ativo"""
    print(f"\n🔄 Monitoramento ativo (verificação a cada {intervalo}s)")
    print("🛑 Para parar: Pressione Ctrl+C")
    print("=" * 50)
    
    restart_count = 0
    max_restarts = 5
    
    try:
        while True:
            time.sleep(intervalo)
            
            # Verificar se processo ainda está rodando
            if processo.poll() is not None:
                print("⚠️ Servidor parou! Tentando reiniciar...")
                
                if restart_count < max_restarts:
                    restart_count += 1
                    print(f"🔄 Tentativa {restart_count}/{max_restarts}")
                    
                    time.sleep(5)
                    novo_processo = iniciar_servidor()
                    
                    if novo_processo:
                        print("✅ Servidor reiniciado com sucesso!")
                        processo = novo_processo
                        restart_count = 0
                    else:
                        print("❌ Falha ao reiniciar")
                else:
                    print("❌ Limite de restarts atingido")
                    break
            else:
                # Verificar se está respondendo
                try:
                    response = requests.get("http://localhost:8000", timeout=5)
                    if response.status_code != 200:
                        print("⚠️ Servidor não está respondendo adequadamente")
                except:
                    print("⚠️ Servidor não está respondendo")
                    
    except KeyboardInterrupt:
        print("\n🛑 Parando servidor...")
        processo.terminate()
        processo.wait()
        print("✅ Servidor parado com sucesso")

def mostrar_opcoes_tunnel():
    """Mostrar opções para acesso global"""
    print("\n🌍 OPÇÕES PARA ACESSO GLOBAL:")
    print("=" * 50)
    print("1. 📡 NGROK (Recomendado):")
    print("   • Site: https://ngrok.com")
    print("   • Comando: ngrok http 8001")
    print()
    print("2. 🔗 SERVEO (SSH - Gratuito):")
    print("   • Comando: ssh -R 80:localhost:8000 serveo.net")
    print()
    print("3. ☁️ CLOUDFLARE TUNNEL:")
    print("   • Comando: cloudflared tunnel --url http://localhost:8000")
    print()
    print("4. 🔧 LOCALTUNNEL:")
    print("   • Instalar: npm install -g localtunnel")
    print("   • Comando: lt --port 8000")

def main():
    """Função principal"""
    print("🐘 MAMUTE - SERVIDOR AUTOMÁTICO")
    print("🚀 Servidor Local + Opções de Túnel Global")
    print("=" * 60)
    
    # Verificar se PostgreSQL está disponível
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
        print("✅ PostgreSQL conectado")
    except Exception as e:
        print(f"⚠️ PostgreSQL: {e}")
        print("   Sistema funcionará em modo limitado")
    
    # Iniciar servidor
    processo = iniciar_servidor()
    
    if processo:
        # Mostrar opções de túnel
        mostrar_opcoes_tunnel()
        
        # Monitorar servidor
        monitorar_servidor(processo)
    else:
        print("❌ Falha ao iniciar sistema")
        return False
    
    return True

if __name__ == "__main__":
    main()