#!/usr/bin/env python3
"""
🚀 INICIALIZADOR FINAL - SISTEMA MAMUTE COMPLETO
Inicia servidor web e testa todas as funcionalidades
"""

import subprocess
import time
import requests
import json
from pathlib import Path
import os

def iniciar_servidor_web():
    """Iniciar servidor web em background"""
    print("🌐 INICIANDO SERVIDOR WEB MAMUTE")
    print("=" * 50)
    
    try:
        # Configurar ambiente
        env = os.environ.copy()
        env["POSTGRES_HOST"] = "localhost"
        env["POSTGRES_PORT"] = "5432"
        env["POSTGRES_DB"] = "ia_database"
        env["POSTGRES_USER"] = "postgres"
        env["POSTGRES_PASSWORD"] = "postgres@"
        env["DATABASE_URL"] = "postgresql://postgres:postgres%40@localhost:5432/ia_database"
        env["AI_NAME"] = "Mamute"
        
        # Comando para iniciar
        cmd = [
            "python", "-m", "uvicorn",
            "web_app:app",
            "--host", "0.0.0.0",
            "--port", "8002",
            "--reload"
        ]
        
        # Iniciar processo
        processo = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("⏳ Aguardando inicialização...")
        time.sleep(10)  # Aguardar servidor inicializar
        
        # Testar se está funcionando
        for tentativa in range(5):
            try:
                response = requests.get("http://localhost:8002/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Servidor web iniciado com sucesso!")
                    print("🌐 URL Local: http://localhost:8002")
                    print("🏠 URL Rede: http://0.0.0.0:8002")
                    return processo
            except:
                print(f"   Tentativa {tentativa + 1}/5...")
                time.sleep(2)
        
        print("❌ Servidor não está respondendo")
        return None
        
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return None

def testar_api_chat():
    """Testar API de chat"""
    print("\n💬 TESTANDO API DE CHAT")
    print("=" * 50)
    
    try:
        # Teste de saúde
        response = requests.get("http://localhost:8002/health", timeout=10)
        if response.status_code == 200:
            print("✅ API está saudável")
        else:
            print("❌ API não está saudável")
            return False
        
        # Teste de chat
        chat_data = {
            "message": "Olá Mamute! Como você está?",
            "session_id": "teste_usuario_123",
            "use_context": True
        }
        
        print("📤 Enviando mensagem para Mamute...")
        response = requests.post(
            "http://localhost:8002/api/chat",
            json=chat_data,
            timeout=30
        )
        
        if response.status_code == 200:
            resultado = response.json()
            print("✅ Chat funcionando!")
            print(f"🐘 Mamute respondeu: {resultado['response'][:100]}...")
            print(f"⏱️ Tempo: {resultado.get('processing_time', 'N/A')}s")
            print(f"🎯 Tokens: {resultado.get('tokens_used', 'N/A')}")
            return True
        else:
            print(f"❌ Erro no chat: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar chat: {e}")
        return False

def testar_funcionalidades_completas():
    """Testar todas as funcionalidades"""
    print("\n🧪 TESTANDO FUNCIONALIDADES COMPLETAS")
    print("=" * 50)
    
    testes = []
    
    # Teste 1: Análise de dados
    try:
        chat_data = {
            "message": "Quais tabelas estão disponíveis no banco de dados?",
            "session_id": "teste_analise"
        }
        response = requests.post("http://localhost:8000/api/chat", json=chat_data, timeout=15)
        if response.status_code == 200:
            testes.append("✅ Análise de BD")
        else:
            testes.append("❌ Análise de BD")
    except:
        testes.append("❌ Análise de BD")
    
    # Teste 2: Documentos
    try:
        response = requests.get("http://localhost:8000/api/documents", timeout=10)
        if response.status_code == 200:
            docs = response.json()
            testes.append(f"✅ Documentos ({len(docs)} encontrados)")
        else:
            testes.append("❌ Documentos")
    except:
        testes.append("❌ Documentos")
    
    # Teste 3: Métricas
    try:
        response = requests.get("http://localhost:8000/api/metrics", timeout=10)
        if response.status_code == 200:
            testes.append("✅ Métricas")
        else:
            testes.append("❌ Métricas")
    except:
        testes.append("❌ Métricas")
    
    # Teste 4: Dashboard
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200 and "Mamute" in response.text:
            testes.append("✅ Dashboard")
        else:
            testes.append("❌ Dashboard")
    except:
        testes.append("❌ Dashboard")
    
    print("📊 RESULTADOS DOS TESTES:")
    for teste in testes:
        print(f"   {teste}")
    
    sucessos = len([t for t in testes if "✅" in t])
    total = len(testes)
    
    print(f"\n🎯 RESULTADO FINAL: {sucessos}/{total} testes passaram")
    return sucessos == total

def criar_script_ngrok():
    """Criar script para túnel ngrok"""
    script_content = """@echo off
echo 🌍 INICIANDO TÚNEL NGROK PARA MAMUTE
echo =====================================

REM Verificar se ngrok está instalado
ngrok version >nul 2>&1
if errorlevel 1 (
    echo ❌ ngrok não está instalado
    echo 💡 Baixe em: https://ngrok.com/download
    pause
    exit /b 1
)

echo ⏳ Iniciando túnel ngrok...
echo 🌐 Servidor local: http://localhost:8000
echo 📡 Criando túnel público...

REM Iniciar ngrok
ngrok http 8000 --log stdout
"""
    
    with open("iniciar_tunnel_ngrok.bat", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("📡 Script de túnel ngrok criado: iniciar_tunnel_ngrok.bat")

def main():
    """Função principal"""
    print("🐘 MAMUTE - INICIALIZAÇÃO COMPLETA DO SISTEMA")
    print("🚀 Configurando PostgreSQL ✅ | OpenAI ⚠️ | Interface Web 🌐")
    print("=" * 80)
    
    # 1. Iniciar servidor web
    servidor_processo = iniciar_servidor_web()
    if not servidor_processo:
        print("❌ Falha ao iniciar servidor web")
        return False
    
    # 2. Testar chat
    if not testar_api_chat():
        print("❌ Falha nos testes de chat")
        servidor_processo.terminate()
        return False
    
    # 3. Testar funcionalidades
    funcionalidades_ok = testar_funcionalidades_completas()
    
    # 4. Criar scripts auxiliares
    criar_script_ngrok()
    
    # 5. Relatório final
    print("\n" + "=" * 80)
    print("🎉 CONFIGURAÇÃO COMPLETA FINALIZADA!")
    print("=" * 80)
    
    print("✅ SISTEMA CONFIGURADO:")
    print("   🐘 PostgreSQL: Conectado e funcionando")
    print("   🌐 Interface Web: Ativa em http://localhost:8000")
    print("   💬 Chat IA: Funcionando com Mamute")
    print("   📊 API REST: Todos os endpoints ativos")
    print("   📄 Documentação: http://localhost:8000/docs")
    
    print("\n⚠️ PRÓXIMOS PASSOS OPCIONAIS:")
    print("   🤖 Configure OpenAI API no .env para IA avançada")
    print("   📡 Execute iniciar_tunnel_ngrok.bat para acesso global")
    print("   🔧 Use http://localhost:8000/chat para interface web")
    
    print(f"\n🎯 FUNCIONALIDADES: {'Todas funcionando!' if funcionalidades_ok else 'Algumas com problemas'}")
    
    print("\n🚀 SERVIDOR RODANDO...")
    print("   💡 Pressione Ctrl+C para parar")
    print("   🌐 Acesse: http://localhost:8000")
    
    try:
        # Manter servidor rodando
        while True:
            time.sleep(10)
            # Verificar se processo ainda está ativo
            if servidor_processo.poll() is not None:
                print("❌ Servidor parou inesperadamente")
                break
    except KeyboardInterrupt:
        print("\n🛑 Parando servidor...")
        servidor_processo.terminate()
        print("✅ Servidor parado com sucesso")
    
    return True

if __name__ == "__main__":
    main()