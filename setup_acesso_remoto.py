#!/usr/bin/env python3
"""
Configurador de Acesso Remoto para IA Mamute
Permite acesso de qualquer local via web
"""

import subprocess
import sys
import os
import webbrowser
from threading import Thread
import time

def install_ngrok():
    """Instalar ngrok se necessário"""
    print("🔧 Verificando ngrok...")
    
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        print("✅ ngrok já está instalado!")
        return True
    except FileNotFoundError:
        print("⬇️ Instalando ngrok...")
        
        # Download ngrok
        import urllib.request
        import zipfile
        
        ngrok_url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
        
        print("Baixando ngrok...")
        urllib.request.urlretrieve(ngrok_url, "ngrok.zip")
        
        print("Extraindo...")
        with zipfile.ZipFile("ngrok.zip", 'r') as zip_ref:
            zip_ref.extractall(".")
        
        os.remove("ngrok.zip")
        
        print("✅ ngrok instalado com sucesso!")
        return True

def start_ngrok_tunnel():
    """Iniciar túnel ngrok"""
    print("🚀 Criando túnel público...")
    
    # Iniciar ngrok em background
    ngrok_process = subprocess.Popen(
        ['ngrok', 'http', '8000', '--log=stdout'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Aguardar túnel estar pronto
    print("⏳ Aguardando túnel...")
    time.sleep(5)
    
    # Obter URL público
    try:
        import requests
        response = requests.get('http://localhost:4040/api/tunnels')
        tunnels = response.json()['tunnels']
        
        if tunnels:
            public_url = tunnels[0]['public_url']
            print(f"🌍 SUCESSO! Sua IA está disponível globalmente em:")
            print(f"🔗 {public_url}")
            print(f"🔗 {public_url}/chat")
            
            # Abrir no navegador
            webbrowser.open(public_url)
            
            return public_url, ngrok_process
    except:
        print("ℹ️ Acesse http://localhost:4040 para ver a URL pública")
        return None, ngrok_process

def start_local_server():
    """Iniciar servidor local em background"""
    print("🐘 Iniciando servidor IA Mamute...")
    
    server_process = subprocess.Popen(
        [sys.executable, 'web_app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("⏳ Aguardando servidor...")
    time.sleep(8)
    print("✅ Servidor local rodando!")
    
    return server_process

def main():
    """Função principal"""
    print("🌐 " + "="*60)
    print("🌐 CONFIGURADOR DE ACESSO REMOTO - IA MAMUTE")
    print("🌐 Torne sua IA acessível de qualquer lugar do mundo!")
    print("🌐 " + "="*60)
    print()
    
    # Opções de acesso
    print("📋 OPÇÕES DE ACESSO:")
    print("1. 🏠 Rede Local (LAN) - Mesmo WiFi")
    print("2. 🌍 Internet Global - Qualquer lugar do mundo")
    print("3. 📊 Status dos serviços")
    
    choice = input("\n🎯 Escolha uma opção (1-3): ").strip()
    
    if choice == "1":
        print("\n🏠 ACESSO NA REDE LOCAL")
        print("─" * 40)
        print("✅ Seu servidor já está configurado!")
        print(f"🔗 URL Local: http://192.168.1.70:8000")
        print(f"💬 Chat: http://192.168.1.70:8000/chat")
        print("\n📱 Use essas URLs em qualquer dispositivo na mesma rede!")
        
        # Iniciar servidor se necessário
        start_choice = input("\n🚀 Iniciar servidor agora? (s/n): ").lower()
        if start_choice == 's':
            start_local_server()
            print("🎉 Servidor rodando! Acesse as URLs acima.")
            
    elif choice == "2":
        print("\n🌍 ACESSO GLOBAL VIA INTERNET")
        print("─" * 40)
        
        # Instalar ngrok
        if install_ngrok():
            # Iniciar servidor local
            server_proc = start_local_server()
            
            # Criar túnel público
            public_url, ngrok_proc = start_ngrok_tunnel()
            
            if public_url:
                print(f"\n🎉 PRONTO! Sua IA Mamute está online globalmente!")
                print(f"🌐 Compartilhe essa URL com qualquer pessoa:")
                print(f"🔗 {public_url}")
                print(f"💬 Chat direto: {public_url}/chat")
                print("\n⚠️ Mantenha este terminal aberto para manter o acesso!")
                
                input("\n⏸️ Pressione Enter para encerrar...")
                
                # Cleanup
                ngrok_proc.terminate()
                server_proc.terminate()
            
    elif choice == "3":
        print("\n📊 STATUS DOS SERVIÇOS")
        print("─" * 40)
        
        # Verificar servidor local
        try:
            import requests
            response = requests.get('http://localhost:8000/health', timeout=3)
            print("✅ Servidor local: ONLINE")
            print(f"🔗 http://localhost:8000")
            print(f"🔗 http://192.168.1.70:8000")
        except:
            print("❌ Servidor local: OFFLINE")
        
        # Verificar ngrok
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=3)
            tunnels = response.json()['tunnels']
            if tunnels:
                print("✅ Túnel público: ATIVO")
                print(f"🌐 {tunnels[0]['public_url']}")
            else:
                print("⭕ Túnel público: SEM TÚNEIS")
        except:
            print("❌ Túnel público: INATIVO")
    
    else:
        print("❌ Opção inválida!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Cancelado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")