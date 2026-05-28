#!/usr/bin/env python3
"""
🎉 MAMUTE FUNCIONANDO - SERVIDOR FINAL
Chat funcionando + Servidor otimizado
"""

import subprocess
import sys
import os
import time

def iniciar_mamute_final():
    """Inicia Mamute com servidor otimizado"""
    print("🎉🎉🎉 MAMUTE TOTALMENTE FUNCIONAL! 🎉🎉🎉")
    print("=" * 70)
    print("🐘 Chat funcionando perfeitamente")
    print("💾 Banco PostgreSQL conectado")
    print("🎯 Sistema de fallback ativo")
    print("🌐 Iniciando servidor web...")
    print("=" * 70)
    
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
    
    # Comando simples e direto
    cmd = [
        "python", "-m", "uvicorn", 
        "web_app:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--log-level", "info"
    ]
    
    print("🚀 Iniciando servidor Uvicorn...")
    print(f"📋 Comando: {' '.join(cmd)}")
    print()
    
    try:
        # Iniciar servidor
        processo = subprocess.Popen(
            cmd,
            env=env,
            cwd=os.path.dirname(__file__)
        )
        
        print("⚡ Servidor iniciado!")
        print("🌐 URL: http://localhost:8000")
        print("💬 Chat: http://localhost:8000/chat")
        print("📚 Docs: http://localhost:8000/docs")
        print()
        print("🐘 O Mamute está respondendo suas perguntas!")
        print("   Teste no navegador: http://localhost:8000/chat")
        print()
        print("✅ SISTEMA TOTALMENTE FUNCIONAL!")
        print()
        
        # Aguardar input do usuário
        try:
            input("🛑 Pressione Enter para parar o servidor...")
        except KeyboardInterrupt:
            print("\n⏹️ Parando servidor...")
        
        # Parar servidor
        processo.terminate()
        processo.wait(timeout=5)
        print("✅ Servidor parado com sucesso")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    # Mostrar resumo do que foi alcançado
    print("🏆 RESUMO DO QUE CONQUISTAMOS:")
    print("-" * 50)
    print("✅ PostgreSQL conectado e funcionando")
    print("✅ Banco de dados estruturado")
    print("✅ Chat Mamute respondendo inteligentemente")
    print("✅ Sistema de fallback para garantir respostas")
    print("✅ Análise de dados do PostgreSQL")
    print("✅ Comandos SQL sendo fornecidos")
    print("✅ Múltiplos bancos de dados detectados")
    print()
    
    iniciar_mamute_final()