import subprocess
import sys
import os

def check_postgres():
    try:
        # Tenta conectar ao serviço do PostgreSQL
        import psycopg2
        import dotenv
        from pathlib import Path
        dotenv.load_dotenv(dotenv.find_dotenv())
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            return False, "DATABASE_URL não configurada no .env"
        conn = psycopg2.connect(db_url)
        conn.close()
        return True, "PostgreSQL OK"
    except Exception as e:
        return False, f"Erro PostgreSQL: {e}"

def check_python_services():
    # Verifica se algum processo Python relacionado à IA está rodando ou escutando na porta 8002
    try:
        import psutil
        porta_alvo = 8002
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'connections']):
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmd = ' '.join(proc.info.get('cmdline') or [])
                # Checa nome do script
                if 'servidor' in cmd or 'web_app' in cmd or 'mamute' in cmd:
                    return True, f"Serviço Python ativo: {cmd}"
                # Checa conexões na porta 8002
                try:
                    for conn in proc.connections(kind='inet'):
                        if conn.status == psutil.CONN_LISTEN and conn.laddr.port == porta_alvo:
                            return True, f"Python escutando na porta {porta_alvo}: {cmd}"
                except Exception:
                    continue
        return False, "Nenhum serviço Python IA ativo na porta 8002"
    except Exception as e:
        return False, f"Erro ao checar serviços Python: {e}"

def check_cloudflare_tunnel():
    # Verifica se o túnel Cloudflare está ativo
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] and 'cloudflared' in proc.info['name'].lower():
                return True, "Cloudflare Tunnel ativo"
        return False, "Cloudflare Tunnel não encontrado"
    except Exception as e:
        return False, f"Erro ao checar Cloudflare Tunnel: {e}"

def main():
    print("--- Diagnóstico IA 24/7 ---")
    ok_pg, msg_pg = check_postgres()
    print(f"[PostgreSQL] {msg_pg}")
    ok_py, msg_py = check_python_services()
    print(f"[Python IA] {msg_py}")
    ok_cf, msg_cf = check_cloudflare_tunnel()
    print(f"[Cloudflare Tunnel] {msg_cf}")
    if ok_pg and ok_py and ok_cf:
        print("\n✅ IA 100% ONLINE em todos os serviços!")
        sys.exit(0)
    else:
        print("\n❌ Algum serviço está offline. Veja os detalhes acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()
