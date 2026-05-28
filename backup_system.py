import os
import sys
import subprocess
import shutil
import gzip
import json
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import time
from threading import Thread

# Tentar importar schedule, usar fallback se não disponível
try:
    import schedule
    schedule_available: bool = True
except ImportError:
    schedule = None
    schedule_available: bool = False

# Adicionar o diretório principal ao path
ROOT_DIR: Path = Path(__file__).resolve().parent
SRC_DIR: Path = ROOT_DIR / "src"
APPS_DIR: Path = SRC_DIR / "apps"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.database.connection import DatabaseManager


class MamuteBackupSystem:
    """Sistema completo de backup para o Mamute"""
    
    def __init__(self, config_file: str = ".env"):
        self.config = Config(config_file)
        self.logger = setup_logger("MamuteBackup")
        self.db_manager = DatabaseManager(self.config)
        
        # Diretórios de backup
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        self.db_backup_dir = self.backup_dir / "database"
        self.files_backup_dir = self.backup_dir / "files"
        self.config_backup_dir = self.backup_dir / "config"
        
        for dir_path in [self.db_backup_dir, self.files_backup_dir, self.config_backup_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.logger.info("Sistema de backup do Mamute inicializado")
    
    def create_database_backup(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        try:
            if not backup_name:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"mamute_db_{timestamp}"
            
            backup_file = self.db_backup_dir / f"{backup_name}.sql"
            compressed_file = self.db_backup_dir / f"{backup_name}.sql.gz"
            
            dump_cmd: List[str] = [
                "pg_dump",
                "--host", self.config.postgres_host or "",
                "--port", str(self.config.postgres_port or ""),
                "--username", self.config.postgres_user or "",
                "--dbname", self.config.postgres_db or "",
                "--verbose",
                "--clean",
                "--if-exists",
                "--create",
                "--format=plain",
                "--file", str(backup_file)
            ]
            
            env = os.environ.copy()
            if self.config.postgres_password is not None:
                env['PGPASSWORD'] = self.config.postgres_password
            
            self.logger.info(f"Iniciando backup do banco: {backup_name}")
            
            subprocess.run(dump_cmd, env=env, capture_output=True, text=True, check=True)
            
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            backup_file.unlink()
            backup_size = compressed_file.stat().st_size
            
            metadata: Dict[str, Any] = {
                'backup_name': backup_name,
                'backup_type': 'database',
                'created_at': datetime.datetime.now().isoformat(),
                'file_path': str(compressed_file),
                'file_size': backup_size,
                'file_size_mb': round(backup_size / (1024*1024), 2),
                'database_info': {
                    'host': self.config.postgres_host,
                    'port': self.config.postgres_port,
                    'database': self.config.postgres_db,
                    'user': self.config.postgres_user
                },
                'status': 'completed'
            }
            
            metadata_file = self.db_backup_dir / f"{backup_name}.meta.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Backup do banco concluído: {compressed_file} ({metadata['file_size_mb']} MB)")
            return metadata
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Erro no pg_dump: {e.stderr}"
            self.logger.error(error_msg)
            return {'backup_name': backup_name, 'status': 'failed', 'error': error_msg, 'created_at': datetime.datetime.now().isoformat()}
        except Exception as e:
            error_msg = f"Erro no backup do banco: {str(e)}"
            self.logger.error(error_msg)
            return {'backup_name': backup_name, 'status': 'failed', 'error': error_msg, 'created_at': datetime.datetime.now().isoformat()}
    
    def create_files_backup(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        try:
            if not backup_name:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"mamute_files_{timestamp}"
            
            backup_file = self.files_backup_dir / f"{backup_name}.tar.gz"
            
            important_paths: List[str] = [
                "src/",
                "web/",
                "requirements.txt",
                "main.py",
                "web_app.py",
                "*.py",
                "*.md",
                "*.sh",
                "*.bat"
            ]
            
            self.logger.info(f"Iniciando backup de arquivos: {backup_name}")
            
            import tarfile, glob
            with tarfile.open(backup_file, "w:gz") as tar:
                for path_pattern in important_paths:
                    if "*" in path_pattern:
                        for file_path in glob.glob(path_pattern):
                            if os.path.exists(file_path):
                                tar.add(file_path)
                                self.logger.debug(f"Adicionado ao backup: {file_path}")
                    else:
                        if os.path.exists(path_pattern):
                            tar.add(path_pattern)
                            self.logger.debug(f"Adicionado ao backup: {path_pattern}")
            
            backup_size = backup_file.stat().st_size
            
            metadata: Dict[str, Any] = {
                'backup_name': backup_name,
                'backup_type': 'files',
                'created_at': datetime.datetime.now().isoformat(),
                'file_path': str(backup_file),
                'file_size': backup_size,
                'file_size_mb': round(backup_size / (1024*1024), 2),
                'included_paths': important_paths,
                'status': 'completed'
            }
            
            metadata_file = self.files_backup_dir / f"{backup_name}.meta.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Backup de arquivos concluído: {backup_file} ({metadata['file_size_mb']} MB)")
            return metadata
            
        except Exception as e:
            error_msg = f"Erro no backup de arquivos: {str(e)}"
            self.logger.error(error_msg)
            return {'backup_name': backup_name, 'status': 'failed', 'error': error_msg, 'created_at': datetime.datetime.now().isoformat()}
    
    def create_config_backup(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Criar backup das configurações"""
        try:
            if not backup_name:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"mamute_config_{timestamp}"

            config_backup: Dict[str, Any] = {
                'backup_info': {
                    'name': backup_name,
                    'created_at': datetime.datetime.now().isoformat(),
                    'system': 'Mamute IA PostgreSQL',
                    'version': '1.0'
                },
                'database_config': {
                    'host': self.config.postgres_host,
                    'port': self.config.postgres_port,
                    'database': self.config.postgres_db,
                    'user': self.config.postgres_user,
                },
                'ai_config': {
                    'ai_name': getattr(self.config, 'ai_name', None),
                    'max_tokens': getattr(self.config, 'max_tokens', None),
                    'temperature': getattr(self.config, 'temperature', None),
                    'debug': getattr(self.config, 'debug', None),
                    'log_level': getattr(self.config, 'log_level', None)
                },
                'environment_vars': {
                    k: v for k, v in os.environ.items()
                    if k.startswith(('AI_', 'POSTGRES_', 'DATABASE_', 'MAX_', 'TEMPERATURE', 'DEBUG', 'LOG_'))
                    and 'PASSWORD' not in k and 'KEY' not in k
                }
            }

            backup_file = self.config_backup_dir / f"{backup_name}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(config_backup, f, indent=2, ensure_ascii=False)

            backup_size = backup_file.stat().st_size

            metadata: Dict[str, Any] = {
                'backup_name': backup_name,
                'backup_type': 'config',
                'created_at': datetime.datetime.now().isoformat(),
                'file_path': str(backup_file),
                'file_size': backup_size,
                'file_size_kb': round(backup_size / 1024, 2),
                'status': 'completed'
            }

            self.logger.info(f"Backup de configurações concluído: {backup_file}")
            return metadata

        except Exception as e:
            error_msg = f"Erro no backup de configurações: {str(e)}"
            self.logger.error(error_msg)
            return {
                'backup_name': backup_name if 'backup_name' in locals() else None,
                'status': 'failed',
                'error': error_msg,
                'created_at': datetime.datetime.now().isoformat()
            }
    
    def create_full_backup(self, backup_name: Optional[str] = None) -> Dict[str, Any]:
        """Criar backup completo (banco + arquivos + configurações)"""
        try:
            if not backup_name:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"mamute_full_{timestamp}"

            self.logger.info(f"Iniciando backup completo: {backup_name}")

            db_result: Dict[str, Any] = self.create_database_backup(f"{backup_name}_db")
            files_result: Dict[str, Any] = self.create_files_backup(f"{backup_name}_files")
            config_result: Dict[str, Any] = self.create_config_backup(f"{backup_name}_config")

            full_backup_info: Dict[str, Any] = {
                'backup_name': backup_name,
                'backup_type': 'full',
                'created_at': datetime.datetime.now().isoformat(),
                'components': {
                    'database': db_result,
                    'files': files_result,
                    'config': config_result
                },
                'status': 'completed' if all(
                    r.get('status') == 'completed'
                    for r in [db_result, files_result, config_result]
                ) else 'partial',
                'total_size_mb': sum(
                    r.get('file_size_mb', r.get('file_size_kb', 0))
                    for r in [db_result, files_result, config_result]
                    if r.get('status') == 'completed'
                )
            }

            full_backup_file = self.backup_dir / f"{backup_name}_full.json"
            with open(full_backup_file, 'w', encoding='utf-8') as f:
                json.dump(full_backup_info, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Backup completo finalizado: {backup_name}")
            self.logger.info(f"Status: {full_backup_info['status']}")
            self.logger.info(f"Tamanho total: {full_backup_info['total_size_mb']:.2f} MB")

            return full_backup_info

        except Exception as e:
            error_msg = f"Erro no backup completo: {str(e)}"
            self.logger.error(error_msg)
            return {
                'backup_name': backup_name,
                'status': 'failed',
                'error': error_msg,
                'created_at': datetime.datetime.now().isoformat()
            }
    
    def list_backups(self, backup_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Listar todos os backups disponíveis"""
        try:
            backups: List[Dict[str, Any]] = []

            search_dirs: List[Any] = []
            if backup_type == 'database' or backup_type is None:
                search_dirs.append((self.db_backup_dir, 'database'))
            if backup_type == 'files' or backup_type is None:
                search_dirs.append((self.files_backup_dir, 'files'))
            if backup_type == 'config' or backup_type is None:
                search_dirs.append((self.config_backup_dir, 'config'))
            if backup_type == 'full' or backup_type is None:
                search_dirs.append((self.backup_dir, 'full'))

            for search_dir, btype in search_dirs:
                if btype == 'full':
                    pattern = "*_full.json"
                else:
                    pattern = "*.meta.json"

                for meta_file in search_dir.glob(pattern):
                    try:
                        with open(meta_file, 'r', encoding='utf-8') as f:
                            backup_info: Dict[str, Any] = json.load(f)
                        backup_info['backup_type'] = btype
                        backups.append(backup_info)
                    except Exception as e:
                        self.logger.warning(f"Erro ao ler metadata {meta_file}: {e}")

            backups.sort(
                key=lambda x: x.get('created_at', ''),
                reverse=True
            )

            return backups

        except Exception as e:
            self.logger.error(f"Erro ao listar backups: {e}")
            return []
    
    def delete_old_backups(self, days_to_keep: int = 7) -> Dict[str, Any]:
        """Remover backups antigos"""
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
            deleted_backups: List[str] = []
            deleted_size: int = 0

            all_backups: List[Dict[str, Any]] = self.list_backups()

            for backup in all_backups:
                try:
                    backup_date = datetime.datetime.fromisoformat(
                        backup['created_at'].replace('Z', '+00:00').replace('+00:00', '')
                    )

                    if backup_date < cutoff_date:
                        file_path = backup.get('file_path')
                        if file_path and os.path.exists(file_path):
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            deleted_size += file_size

                            meta_file = file_path.replace('.sql.gz', '.meta.json').replace('.tar.gz', '.meta.json').replace('.json', '.meta.json')
                            if os.path.exists(meta_file) and meta_file != file_path:
                                os.remove(meta_file)

                            deleted_backups.append(backup['backup_name'])
                            self.logger.info(f"Backup removido: {backup['backup_name']}")

                except Exception as e:
                    self.logger.warning(f"Erro ao processar backup {backup.get('backup_name', 'unknown')}: {e}")

            result: Dict[str, Any] = {
                'deleted_count': len(deleted_backups),
                'deleted_backups': deleted_backups,
                'freed_space_mb': round(deleted_size / (1024*1024), 2),
                'cutoff_date': cutoff_date.isoformat(),
                'operation_date': datetime.datetime.now().isoformat()
            }

            self.logger.info(f"Limpeza concluída: {result['deleted_count']} backups removidos, {result['freed_space_mb']} MB liberados")

            return result

        except Exception as e:
            error_msg = f"Erro na limpeza de backups: {str(e)}"
            self.logger.error(error_msg)
            return {'error': error_msg}
    
    def schedule_automatic_backups(self):
        """Configurar backups automáticos"""
        if not schedule_available or schedule is None:
            self.logger.warning("Biblioteca 'schedule' não disponível - instale com: pip install schedule")
            self.logger.info("Agendamento automático desabilitado")
            return

        def run_scheduled_backup():
            self.logger.info("Executando backup automático agendado")
            result = self.create_full_backup()
            if result.get('status') == 'completed':
                self.logger.info("Backup automático concluído com sucesso")
                self.delete_old_backups(7)
            else:
                self.logger.error("Backup automático falhou")

        def run_scheduler():
            while True:
                if schedule is not None:
                    schedule.run_pending()
                time.sleep(60)

        if schedule is not None:
            schedule.every().day.at("02:00").do(run_scheduled_backup)
            schedule.every(6).hours.do(lambda: self.create_database_backup())

        scheduler_thread = Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()

        self.logger.info("Sistema de backups automáticos iniciado")
        self.logger.info("- Backup completo: Diariamente às 02:00")
        self.logger.info("- Backup do banco: A cada 6 horas")
        self.logger.info("- Limpeza automática: Manter apenas últimos 7 dias")
        
    # ...existing code...

def main():
    """Função principal para executar sistema de backup"""
    print("🐘 SISTEMA DE BACKUP DO MAMUTE")
    print("=" * 50)
    try:
        backup_system = MamuteBackupSystem()
        print("📦 Criando backup completo...")
        result = backup_system.create_full_backup()
        print(f"✅ Status: {result.get('status', 'unknown')}")
        if result.get('status') == 'completed':
            print(f"📊 Tamanho total: {result.get('total_size_mb', 0):.2f} MB")
        print("\n📋 Backups disponíveis:")
        backups = backup_system.list_backups()
        for backup in backups[:5]:
            print(f"- {backup['backup_name']} ({backup['backup_type']}) - {backup.get('created_at', 'N/A')}")
        print("\n✅ Sistema de backup configurado!")
        print("💡 Para backups automáticos, execute: python -c \"from backup_system import *; backup_system.schedule_automatic_backups()\"")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()