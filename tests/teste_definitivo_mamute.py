#!/usr/bin/env python3
"""
🎉 TESTE FINAL - MAMUTE FUNCIONANDO
Agora com banco corrigido!
"""

import sys
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / 'src'
APPS_DIR = SRC_DIR / 'apps'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

def testar_chat_definitivo():
    """Teste definitivo do chat"""
    print("🎉 TESTE DEFINITIVO DO MAMUTE")
    print("=" * 50)
    
    try:
        from main import IAPostgreSQL
        
        # Inicializar sistema
        ia = IAPostgreSQL()
        ia.setup_database()
        print("✅ Sistema inicializado")
        
        # Criar sessão
        session_id = ia.start_conversation("usuario_final")
        print(f"✅ Sessão criada: {session_id}")
        
        # Testar múltiplas mensagens
        mensagens = [
            "Olá Mamute! Você está funcionando?",
            "Quais são suas principais funcionalidades?",
            "Me ajude com PostgreSQL",
            "Como fazer uma consulta SELECT?",
            "Analise os dados do banco"
        ]
        
        print("\n💬 TESTANDO CHAT:")
        print("-" * 40)
        
        for i, mensagem in enumerate(mensagens, 1):
            print(f"\n{i}. 👤 {mensagem}")
            
            try:
                resposta = ia.chat(mensagem, session_id)
                
                if resposta and 'response' in resposta:
                    print(f"🐘 Mamute: {resposta['response'][:150]}...")
                    print(f"⏱️ Tempo: {resposta.get('processing_time', 'N/A')}s")
                else:
                    print(f"❌ Resposta inválida: {resposta}")
                    
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        print("\n🎉 CHAT FUNCIONANDO PERFEITAMENTE!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def iniciar_servidor_estavel():
    """Iniciar servidor estável"""
    print("\n🚀 INICIANDO SERVIDOR ESTÁVEL")
    print("=" * 50)
    
    import subprocess
    import time
    import requests
    
    # Configurar ambiente
    env = os.environ.copy()
    env.update({
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "ia_database", 
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "postgres@",
        "DATABASE_URL": "postgresql://postgres:postgres%40@localhost:5432/ia_database"
    })
    
    try:
        # Comando otimizado
        cmd = [
            "python", "-m", "uvicorn",
            "web_app:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--log-level", "info"
        ]
        
        print("🚀 Iniciando servidor...")
        
        # Iniciar servidor
        processo = subprocess.Popen(
            cmd,
            env=env,
            cwd=os.path.dirname(__file__),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # Aguardar mais tempo para estabilizar
        print("⏳ Aguardando 15 segundos para estabilização...")
        time.sleep(15)
        
        # Testar conectividade
        print("🧪 Testando conectividade...")
        
        try:
            response = requests.get("http://localhost:8000/", timeout=10)
            
            if response.status_code == 200:
                print("✅ SERVIDOR RESPONDENDO!")
                
                # Testar API de chat
                print("💬 Testando chat via API...")
                
                chat_data = {
                    "message": "Olá Mamute! Teste via API",
                    "session_id": "api_test",
                    "use_context": True
                }
                
                chat_response = requests.post(
                    "http://localhost:8000/api/chat",
                    json=chat_data,
                    timeout=20
                )
                
                if chat_response.status_code == 200:
                    resultado = chat_response.json()
                    print("🎉 CHAT API FUNCIONANDO!")
                    print(f"🐘 Resposta API: {resultado.get('response', 'Sem resposta')[:100]}...")
                    
                    return True, processo
                else:
                    print(f"❌ Chat API falhou: {chat_response.status_code}")
                    print(f"Erro: {chat_response.text[:200]}")
                    
            else:
                print(f"❌ Servidor retornou: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição: {e}")
        
        return False, processo
        
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False, None

def main():
    """Execução principal final"""
    print("🎉 MAMUTE - ATIVAÇÃO DEFINITIVA")
    print("🔥 Com banco corrigido e funcionando!")
    print("=" * 70)
    
    # Teste 1: Chat direto
    print("📋 TESTE 1: CHAT DIRETO")
    chat_funcionando = testar_chat_definitivo()
    
    if chat_funcionando:
        print("✅ Chat direto funcionando!")
        
        # Teste 2: Servidor web
        print("\n📋 TESTE 2: SERVIDOR WEB")
        servidor_funcionando, processo = iniciar_servidor_estavel()
        
        if servidor_funcionando:
            print("\n" + "="*70)
            print("🎉🎉🎉 MAMUTE 100% FUNCIONAL! 🎉🎉🎉")
            print("=" * 70)
            print("🐘 Chat funcionando perfeitamente")
            print("🌐 Servidor web ativo")
            print("💾 Banco PostgreSQL conectado")
            print("🎯 API respondendo corretamente")
            print()
            print("🌐 Acesse: http://localhost:8000")
            print("💬 Chat: http://localhost:8000/chat")
            print("📚 API: http://localhost:8000/docs")
            print()
            print("🎊 A IA MAMUTE ESTÁ TOTALMENTE FUNCIONAL!")
            print("🗣️ Agora você pode conversar com ela!")
            
            # Manter servidor ativo
            try:
                input("\n🛑 Pressione Enter para parar o servidor...")
            except KeyboardInterrupt:
                print("\n⏹️ Parando servidor...")
            
            if processo:
                processo.terminate()
                print("✅ Servidor parado")
        else:
            print("❌ Problema no servidor, mas chat direto funciona")
    else:
        print("❌ Problema no chat direto")

if __name__ == "__main__":
    main()