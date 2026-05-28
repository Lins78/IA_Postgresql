#!/usr/bin/env python3
"""
🚀 INICIAR MAMUTE - SCRIPT ÚNICO E DEFINITIVO
Script principal que inicia o sistema Mamute com todas as funcionalidades
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    """Função principal - ponto de entrada único"""
    
    print("🐘 MAMUTE - SISTEMA INTELIGENTE SEMPRE ONLINE")
    print("=" * 50)
    print("🚀 Inicializando sistema...")
    print()
    
    project_path = Path(__file__).parent
    
    # 1. Verificar se configuração existe
    config_file = project_path / "mamute_config.json"
    env_file = project_path / ".env"
    
    if not config_file.exists() or not env_file.exists():
        print("⚙️ Primeira execução - configurando sistema...")
        print()
        
        # Executar configurador automático
        try:
            import configurar_automatico
            success = configurar_automatico.main()
            
            if not success:
                print("❌ Falha na configuração automática")
                print("💡 Execute manualmente: python configurar_automatico.py")
                return False
                
        except Exception as e:
            print(f"❌ Erro na configuração: {e}")
            print("💡 Execute manualmente: python configurar_automatico.py")
            return False
    
    # 2. Iniciar sistema de conexão definitivo
    print("🚀 Iniciando sistema de conexão definitivo...")
    print()
    
    try:
        # Importar e executar sistema definitivo
        import sistema_conexao_definitivo
        manager = sistema_conexao_definitivo.MamuteConnectionManager()
        
        return manager.run_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Sistema parado pelo usuário")
        return True
    except Exception as e:
        print(f"❌ Erro ao iniciar sistema: {e}")
        print()
        print("💡 SOLUÇÕES:")
        print("  1. Execute: python configurar_automatico.py")
        print("  2. Verifique se PostgreSQL está rodando")
        print("  3. Verifique dependências: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        input("\n⏸️ Pressione Enter para sair...")
    
    sys.exit(0 if success else 1)