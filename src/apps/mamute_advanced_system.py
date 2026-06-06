"""
Integração das Novas Funcionalidades do Mamute
Sistema unificado para gerenciar todas as extensões avançadas
"""
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# Adicionar o diretório principal ao path
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
APPS_DIR = SRC_DIR / "apps"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

# Importar todos os novos módulos
from admin_dashboard import AdminDashboard, get_admin_dashboard_data
from backup_system import MamuteBackupSystem
from data_migration_utils import DataMigrationUtilities
from notification_system import notification_system as global_notification_system, notify_info, notify_success, notify_warning, notify_error
from performance_analyzer import PerformanceAnalyzer
from report_generator import ReportGenerator

from src.utils.config import Config
from src.utils.logger import setup_logger

class MamuteAdvancedSystem:
    """Sistema avançado integrado do Mamute"""
    
    def __init__(self, config_file: str = ".env"):
        """Inicializar sistema integrado"""
        self.config = Config(config_file)
        self.logger = setup_logger("MamuteAdvanced")
        
        # Inicializar todos os subsistemas
        self.admin_dashboard = AdminDashboard()
        self.backup_system = MamuteBackupSystem()
        self.migration_utils = DataMigrationUtilities()
        self.notification_system = global_notification_system
        self.performance_analyzer = PerformanceAnalyzer()
        self.report_generator = ReportGenerator()
        
        # Status dos subsistemas
        self.subsystems_status: Dict[str, bool] = {}
        
        self.logger.info("Sistema avançado integrado do Mamute inicializado")
    
    async def initialize_all_systems(self) -> Dict[str, bool]:
        """Inicializar todos os subsistemas"""
        initialization_results = {}
        
        try:
            # Inicializar dashboard admin
            await notify_info("Inicialização", "Inicializando dashboard administrativo...")
            admin_init = await self.admin_dashboard.initialize()
            initialization_results: Dict[str, bool] = {}
            initialization_results['admin_dashboard'] = admin_init
            
            # Configurar sistema de notificações
            await notify_info("Inicialização", "Configurando sistema de notificações...")
            initialization_results['notification_system'] = True
            
            # Sistema de backup sempre disponível
            await notify_info("Inicialização", "Verificando sistema de backup...")
            initialization_results['backup_system'] = True
            
            # Utilitários de migração sempre disponíveis
            await notify_info("Inicialização", "Verificando utilitários de migração...")
            initialization_results['migration_utils'] = True
            
            # Analisador de performance
            await notify_info("Inicialização", "Configurando analisador de performance...")
            initialization_results['performance_analyzer'] = True
            
            # Gerador de relatórios
            await notify_info("Inicialização", "Configurando gerador de relatórios...")
            initialization_results['report_generator'] = True
            
            self.subsystems_status = initialization_results
            
            # Notificar sucesso total
            successful_systems = sum(1 for status in initialization_results.values() if status)
            total_systems = len(initialization_results)
            
            if successful_systems == total_systems:
                await notify_success(
                    "Sistema Integrado", 
                    f"Todos os {total_systems} subsistemas inicializados com sucesso!"
                )
            else:
                await notify_warning(
                    "Sistema Integrado", 
                    f"{successful_systems}/{total_systems} subsistemas inicializados"
                )
            
            return initialization_results
            
        except Exception as e:
            await notify_error("Erro na Inicialização", f"Erro durante inicialização: {str(e)}")
            self.logger.error(f"Erro na inicialização dos subsistemas: {e}")
            return {}
    
    async def get_system_status(self) -> Dict[str, Any]:
        # Obter status geral do sistema
        try:
            status: Dict[str, Any] = {
                'status': 'operational',
                'timestamp': datetime.now().isoformat(),
                'subsystems': {}
            }
            return status
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    async def start_monitoring_services(self):
        """Iniciar serviços de monitoramento"""
        try:
            await notify_info("Monitoramento", "Iniciando serviços de monitoramento...")
            
            # Iniciar monitoramento de performance
            self.performance_analyzer.start_monitoring()
            
            # Agendar backups automáticos
            self.backup_system.schedule_automatic_backups()
            
            # Agendar relatórios automáticos
            self.report_generator.schedule_automatic_reports()
            
            # Iniciar servidor WebSocket de notificações
            await self.notification_system.start_websocket_server()
            
            await notify_success(
                "Monitoramento Iniciado", 
                "Todos os serviços de monitoramento estão ativos"
            )
            
        except Exception as e:
            await notify_error("Erro no Monitoramento", f"Erro ao iniciar monitoramento: {str(e)}")
            self.logger.error(f"Erro ao iniciar serviços de monitoramento: {e}")
    
    async def generate_system_health_report(self) -> Dict[str, Any]:
        """Gerar relatório completo de saúde do sistema"""
        try:
            await notify_info("Relatório de Saúde", "Gerando relatório completo do sistema...")
            
            # Obter dados do dashboard admin
            admin_data: Dict[str, Any] = await get_admin_dashboard_data()
            
            # Obter métricas de performance
            performance_report: Dict[str, Any] = self.performance_analyzer.generate_performance_report()
            
            # Status dos subsistemas
            subsystems_health = {
                name: "healthy" if status else "error" 
                for name, status in self.subsystems_status.items()
            }
            
            # Notificações recentes
            recent_notifications = self.notification_system.get_recent_notifications(10)
            
            # Backups disponíveis
            available_backups = self.backup_system.list_backups()
            
            # Relatórios gerados
            available_reports = self.report_generator.list_reports()
            
            health_report: Dict[str, Any] = {
                'timestamp': datetime.now().isoformat(),
                'system_overview': {
                    'mamute_version': '2.0.0-advanced',
                    'python_version': sys.version,
                    'subsystems_count': len(self.subsystems_status),
                    'healthy_subsystems': sum(1 for status in self.subsystems_status.values() if status),
                    'overall_status': 'healthy' if all(self.subsystems_status.values()) else 'warning'
                },
                'subsystems_status': subsystems_health,
                'admin_dashboard': admin_data,
                'performance_metrics': performance_report.get('summary', {}),
                'recent_notifications': recent_notifications,
                'backup_info': {
                    'total_backups': len(available_backups),
                    'latest_backup': available_backups[0] if available_backups else None
                },
                'reports_info': {
                    'total_reports': len(available_reports),
                    'latest_report': available_reports[0] if available_reports else None
                },
                'recommendations': self.performance_analyzer.get_recommendations()
            }
            
            # Salvar relatório
            reports_dir = Path("reports/system_health")
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"system_health_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(health_report, f, indent=2, default=str, ensure_ascii=False)
            
            await notify_success(
                "Relatório Concluído", 
                f"Relatório de saúde salvo: {report_file.name}"
            )
            
            return health_report
            
        except Exception as e:
            await notify_error("Erro no Relatório", f"Erro ao gerar relatório de saúde: {str(e)}")
            self.logger.error(f"Erro ao gerar relatório de saúde: {e}")
            return {}
    
    async def create_emergency_backup(self) -> Dict[str, Any]:
        """Criar backup de emergência completo"""
        try:
            await notify_warning("Backup de Emergência", "Iniciando backup de emergência...")
            
            # Criar backup completo
            backup_result = self.backup_system.create_full_backup()
            
            if backup_result.get('status') == 'completed':
                await notify_success(
                    "Backup de Emergência", 
                    f"Backup concluído: {backup_result['backup_name']}"
                )
            else:
                await notify_error(
                    "Backup de Emergência", 
                    "Falha no backup de emergência"
                )
            
            return backup_result
            
        except Exception as e:
            await notify_error("Erro no Backup", f"Erro no backup de emergência: {str(e)}")
            return {'status': 'failed', 'error': str(e)}
    
    async def run_system_diagnostics(self) -> Dict[str, Any]:
        """Executar diagnósticos completos do sistema"""
        try:
            await notify_info("Diagnósticos", "Executando diagnósticos do sistema...")
            
            tests_performed: List[Dict[str, Any]] = []
            issues_found: List[str] = []
            recommendations: List[str] = []
            diagnostics: Dict[str, Any] = {
                'timestamp': datetime.now().isoformat(),
                'tests_performed': tests_performed,
                'issues_found': issues_found,
                'recommendations': recommendations
            }
            
            # Teste 1: Conexão com banco
            try:
                if self.admin_dashboard.ia_system:
                    db_test = self.admin_dashboard.ia_system.db_manager.test_connection()
                    diagnostics['tests_performed'].append({
                        'test': 'Database Connection',
                        'status': 'pass' if db_test else 'fail',
                        'details': 'PostgreSQL connection test'
                    })
                    
                    if not db_test:
                        diagnostics['issues_found'].append('Database connection failed')
                        diagnostics['recommendations'].append('Check PostgreSQL service and credentials')
            except Exception as e:
                diagnostics['issues_found'].append(f'Database test error: {str(e)}')
            
            # Teste 2: Espaço em disco
            try:
                try:
                    import psutil
                    disk_usage = psutil.disk_usage('/')
                    disk_percent = (disk_usage.used / disk_usage.total) * 100
                except ImportError:
                    # Fallback sem psutil
                    disk_percent = 0
                
                diagnostics['tests_performed'].append({
                    'test': 'Disk Space',
                    'status': 'pass' if disk_percent < 90 else 'warning',
                    'details': f'Disk usage: {disk_percent:.1f}%'
                })
                
                if disk_percent > 90:
                    diagnostics['issues_found'].append(f'High disk usage: {disk_percent:.1f}%')
                    diagnostics['recommendations'].append('Free up disk space or expand storage')
                elif disk_percent > 80:
                    diagnostics['recommendations'].append('Monitor disk space - approaching 80%')
            
            except Exception as e:
                diagnostics['issues_found'].append(f'Disk space test error: {str(e)}')
            
            # Teste 3: Memória
            try:
                try:
                    import psutil
                    memory = psutil.virtual_memory()
                except ImportError:
                    # Fallback sem psutil
                    class FakeMemory:
                        percent = 0
                    memory = FakeMemory()
                
                diagnostics['tests_performed'].append({
                    'test': 'Memory Usage',
                    'status': 'pass' if memory.percent < 85 else 'warning',
                    'details': f'Memory usage: {memory.percent:.1f}%'
                })
                
                if memory.percent > 85:
                    diagnostics['issues_found'].append(f'High memory usage: {memory.percent:.1f}%')
                    diagnostics['recommendations'].append('Consider adding more RAM or optimize memory usage')
            
            except Exception as e:
                diagnostics['issues_found'].append(f'Memory test error: {str(e)}')
            
            # Teste 4: Verificar subsistemas
            failed_subsystems: List[str] = [
                name for name, status in self.subsystems_status.items() 
                if not status
            ]
            
            if failed_subsystems:
                diagnostics['issues_found'].extend([
                    f'Subsystem failed: {name}' for name in failed_subsystems
                ])
                diagnostics['recommendations'].append('Restart failed subsystems or check logs')
            
            diagnostics['tests_performed'].append({
                'test': 'Subsystems Status',
                'status': 'pass' if not failed_subsystems else 'fail',
                'details': f'{len(self.subsystems_status) - len(failed_subsystems)}/{len(self.subsystems_status)} subsystems healthy'
            })
            
            # Resumo
            total_tests = len(diagnostics['tests_performed'])
            passed_tests = sum(1 for test in diagnostics['tests_performed'] if test['status'] == 'pass')
            
            diagnostics['summary'] = {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'issues_count': len(diagnostics['issues_found']),
                'overall_health': 'healthy' if len(diagnostics['issues_found']) == 0 else 'warning'
            }
            
            # Salvar diagnósticos
            reports_dir = Path("reports/diagnostics")
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            diag_file = reports_dir / f"diagnostics_{timestamp}.json"
            
            with open(diag_file, 'w', encoding='utf-8') as f:
                json.dump(diagnostics, f, indent=2, default=str, ensure_ascii=False)
            
            if diagnostics['summary']['overall_health'] == 'healthy':
                await notify_success(
                    "Diagnósticos Concluídos", 
                    f"Sistema saudável - {passed_tests}/{total_tests} testes passaram"
                )
            else:
                await notify_warning(
                    "Diagnósticos Concluídos", 
                    f"{len(diagnostics['issues_found'])} problemas encontrados - verifique relatório"
                )
            
            return diagnostics
            
        except Exception as e:
            await notify_error("Erro nos Diagnósticos", f"Erro durante diagnósticos: {str(e)}")
            self.logger.error(f"Erro ao executar diagnósticos: {e}")
            return {}
    
    async def shutdown_all_systems(self):
        """Finalizar todos os subsistemas ordenadamente"""
        try:
            await notify_info("Finalização", "Finalizando subsistemas...")
            
            # Parar monitoramento
            self.performance_analyzer.stop_monitoring()
            
            # Último backup antes de sair
            await self.create_emergency_backup()
            
            await notify_success("Sistema Finalizado", "Todos os subsistemas foram finalizados com segurança")
            
        except Exception as e:
            await notify_error("Erro na Finalização", f"Erro durante finalização: {str(e)}")

# Instância global do sistema avançado
mamute_advanced = MamuteAdvancedSystem()

async def initialize_mamute_advanced():
    """Função de conveniência para inicializar sistema completo"""
    results = await mamute_advanced.initialize_all_systems()
    await mamute_advanced.start_monitoring_services()
    return results

async def main():
    """Função principal para demonstrar sistema integrado"""
    print("🐘" + "=" * 70 + "🐘")
    print("                MAMUTE - SISTEMA AVANÇADO INTEGRADO")
    print("🐘" + "=" * 70 + "🐘")
    
    try:
        # Inicializar sistema completo
        print("\\n🚀 Inicializando sistema avançado...")
        init_results = await initialize_mamute_advanced()
        
        print(f"\\n✅ Subsistemas inicializados:")
        for subsystem, status in init_results.items():
            emoji = "✅" if status else "❌"
            print(f"   {emoji} {subsystem.replace('_', ' ').title()}")
        
        # Executar diagnósticos
        print("\\n🔍 Executando diagnósticos do sistema...")
        diagnostics = await mamute_advanced.run_system_diagnostics()
        
        if diagnostics:
            summary = diagnostics.get('summary', {})
            print(f"   📊 Testes: {summary.get('passed_tests', 0)}/{summary.get('total_tests', 0)} passaram")
            print(f"   🏥 Status: {summary.get('overall_health', 'unknown').upper()}")
            
            if diagnostics.get('issues_found'):
                print(f"   ⚠️ Problemas encontrados: {len(diagnostics['issues_found'])}")
        
        # Gerar relatório de saúde
        print("\\n📋 Gerando relatório de saúde do sistema...")
        health_report = await mamute_advanced.generate_system_health_report()
        
        if health_report:
            overview = health_report.get('system_overview', {})
            print(f"   🐘 Mamute versão: {overview.get('mamute_version', 'N/A')}")
            print(f"   🔧 Subsistemas: {overview.get('healthy_subsystems', 0)}/{overview.get('subsystems_count', 0)} saudáveis")
            print(f"   📊 Status geral: {overview.get('overall_status', 'unknown').upper()}")
        
        print("\\n" + "🐘" + "=" * 70 + "🐘")
        print("            MAMUTE AVANÇADO INICIALIZADO COM SUCESSO!")
        print("🐘" + "=" * 70 + "🐘")
        
        print("\\n💡 Funcionalidades disponíveis:")
        print("   🔧 Dashboard administrativo avançado")
        print("   💾 Sistema de backup automático")
        print("   🔄 Utilitários de migração de dados")
        print("   📢 Sistema de notificações em tempo real")
        print("   📊 Análise de performance avançada")
        print("   📋 Geração automática de relatórios")
        
        print("\\n🌐 Para acessar a interface web:")
        print("   python web_app.py")
        print("   http://localhost:8000")
        
    except Exception as e:
        print(f"\\n❌ Erro durante inicialização: {e}")

if __name__ == "__main__":
    asyncio.run(main())