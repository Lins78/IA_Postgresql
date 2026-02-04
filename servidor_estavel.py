"""
Script para manter o servidor Mamute rodando de forma estável
"""
import subprocess
import sys
import os
import time
import signal

def iniciar_servidor():
    """Inicia o servidor Mamute"""
    print("=" * 60)
    print("🐘 SERVIDOR MAMUTE ESTÁVEL")
    print("=" * 60)
    print("✅ Iniciando servidor web...")
    print("✅ URL: http://localhost:8000")
    print("✅ Pressione Ctrl+C para parar")
    print("=" * 60)
    
    try:
        # Mudar para o diretório do projeto
        os.chdir(r"c:\Users\carlo\Desktop\Projetos\IA_Postgresql")
        
        # Iniciar servidor sem reload
        process = subprocess.Popen([
            ".venv\\Scripts\\python.exe",
            "-m", "uvicorn",
            "web_app:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--log-level", "info"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        # Handler para Ctrl+C
        def signal_handler(sig, frame):
            print("\\n🛑 Parando servidor...")
            process.terminate()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Aguardar inicialização
        time.sleep(3)
        print("🚀 Servidor iniciado! Acesse http://localhost:8000")
        
        # Manter vivo
        while process.poll() is None:
            output = process.stdout.readline()
            if output:
                print(output.strip())
        
    except KeyboardInterrupt:
        print("\\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        if 'process' in locals():
            process.terminate()

if __name__ == "__main__":
    iniciar_servidor()