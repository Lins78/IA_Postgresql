"""
Script para iniciar o servidor web do Mamute
"""
import os
import sys
import subprocess
import webbrowser
from time import sleep

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    try:
        import fastapi
        import uvicorn
        import websockets
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("Execute: pip install fastapi uvicorn websockets")
        return False

def iniciar_servidor():
    """Inicia o servidor web do Mamute"""
    if not verificar_dependencias():
        return
    
    print("=" * 60)
    print("🐘 INICIANDO MAMUTE WEB")
    print("=" * 60)
    print("✅ Sistema: Mamute - IA PostgreSQL")
    print("✅ Servidor: FastAPI + Uvicorn")
    print("✅ URL: http://localhost:8000")
    print("=" * 60)
    
    try:
        # Abrir navegador automaticamente
        print("🌐 Abrindo navegador...")
        sleep(2)
        webbrowser.open("http://localhost:8000")
        
        # Iniciar servidor
        print("🚀 Iniciando servidor web...")
        os.system(".venv\\Scripts\\python.exe web_app.py")
        
    except KeyboardInterrupt:
        print("\\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    iniciar_servidor()