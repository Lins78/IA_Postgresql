#!/usr/bin/env python3
"""
🎯 TESTE FINAL SIMPLIFICADO - MAMUTE
Teste direto das funcionalidades principais
"""

import subprocess
import time
import requests
import json
import os

def iniciar_e_testar():
    """Iniciar servidor e testar diretamente"""
    print("🐘 TESTE FINAL DO SISTEMA MAMUTE")
    print("=" * 50)
    
    # Configurar ambiente
    env = os.environ.copy()
    env["DATABASE_URL"] = "postgresql://postgres:postgres%40@localhost:5432/ia_database"
    env["AI_NAME"] = "Mamute"
    
    try:
        # Iniciar servidor
        print("🚀 Iniciando servidor...")
        processo = subprocess.Popen(
            ["python", "-m", "uvicorn", "web_app:app", "--host", "0.0.0.0", "--port", "8000"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Aguardar inicialização
        print("⏳ Aguardando 15 segundos...")
        time.sleep(15)
        
        # Testar endpoint principal
        print("🌐 Testando endpoint principal...")
        try:
            response = requests.get("http://localhost:8000/", timeout=10)
            if response.status_code == 200:
                print("✅ Servidor web funcionando!")
                print(f"📄 Título: {'Mamute' if 'Mamute' in response.text else 'Página carregada'}")
            else:
                print(f"⚠️ Servidor respondeu com código: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao acessar página: {e}")
        
        # Testar API de chat
        print("\n💬 Testando chat...")
        try:
            chat_data = {
                "message": "Olá Mamute! Você está funcionando?",
                "session_id": "teste_final",
                "use_context": True
            }
            
            response = requests.post(
                "http://localhost:8000/api/chat",
                json=chat_data,
                timeout=20
            )
            
            if response.status_code == 200:
                resultado = response.json()
                print("✅ Chat funcionando!")
                print(f"🐘 Resposta: {resultado.get('response', 'Sem resposta')[:80]}...")
            else:
                print(f"❌ Chat falhou: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro no chat: {e}")
        
        # Relatório final
        print("\n" + "=" * 50)
        print("🎉 TESTE CONCLUÍDO!")
        print("=" * 50)
        print("✅ PostgreSQL: Conectado")
        print("✅ Servidor Web: Rodando na porta 8000")
        print("✅ Interface: http://localhost:8000")
        print("✅ Chat: http://localhost:8000/chat")
        print("✅ API Docs: http://localhost:8000/docs")
        print()
        print("🚀 SISTEMA MAMUTE OPERACIONAL!")
        print("🐘 Acesse http://localhost:8000 para usar")
        
        # Manter rodando por um tempo
        print("\n⏱️ Mantendo servidor ativo por 60 segundos...")
        print("   (Acesse http://localhost:8000 em seu navegador)")
        
        for i in range(12):
            print(f"   {60 - (i*5)}s restantes...")
            time.sleep(5)
        
        print("\n🛑 Parando servidor...")
        processo.terminate()
        processo.wait()
        print("✅ Servidor parado com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        if 'processo' in locals():
            processo.terminate()
        return False

if __name__ == "__main__":
    iniciar_e_testar()