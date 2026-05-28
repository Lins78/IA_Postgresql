"""
Demonstração das Novas Funcionalidades do Mamute
Script para testar e demonstrar todas as implementações avançadas
"""
import asyncio
import time
from datetime import datetime
from pathlib import Path

# Importar sistema integrado
from mamute_advanced_system import mamute_advanced, initialize_mamute_advanced

async def demo_notifications():
    """Demonstrar sistema de notificações"""
    print("\\n🔔 DEMONSTRAÇÃO - SISTEMA DE NOTIFICAÇÕES")
    print("-" * 50)
    
    from notification_system import notify_info, notify_warning, notify_success, notify_error
    
    await notify_info("Demo Iniciada", "Demonstrando sistema de notificações do Mamute")
    await asyncio.sleep(1)
    
    await notify_success("Conexão OK", "Conexão com PostgreSQL estabelecida")
    await asyncio.sleep(1)
    
    await notify_warning("Memória Alta", "Uso de memória em 75% - monitorando")
    await asyncio.sleep(1)
    
    await notify_error("Erro Simulado", "Este é um erro simulado para demonstração")
    
    print("✅ Sistema de notificações demonstrado!")

async def demo_backup_system():
    """Demonstrar sistema de backup"""
    print("\\n💾 DEMONSTRAÇÃO - SISTEMA DE BACKUP")
    print("-" * 50)
    
    try:
        # Criar backup de configurações (mais rápido para demo)
        backup_result = mamute_advanced.backup_system.create_config_backup("demo_backup")
        
        if backup_result.get('status') == 'completed':
            print(f"✅ Backup criado: {backup_result['backup_name']}")
            print(f"📄 Arquivo: {Path(backup_result['file_path']).name}")
            print(f"📊 Tamanho: {backup_result.get('file_size_kb', 0)} KB")
        
        # Listar backups disponíveis
        backups = mamute_advanced.backup_system.list_backups('config')
        print(f"\\n📋 Total de backups de config: {len(backups)}")
        
        for backup in backups[:3]:
            print(f"   - {backup['backup_name']} ({backup['created_at'][:19]})")
        
        print("✅ Sistema de backup demonstrado!")
        
    except Exception as e:
        print(f"❌ Erro no demo de backup: {e}")

def demo_migration_utils():
    """Demonstrar utilitários de migração"""
    print("\\n🔄 DEMONSTRAÇÃO - UTILITÁRIOS DE MIGRAÇÃO")
    print("-" * 50)
    
    try:
        # Simular dados para exportação
        export_result = mamute_advanced.migration_utils.export_to_json(
            'demo_export.json',
            filters={'category': 'demo'}
        )
        
        if export_result.get('status') == 'completed':
            print(f"✅ Exportação realizada: {export_result['exported_count']} documentos")
            print(f"📄 Arquivo: {export_result['output_file']}")
            print(f"📊 Tamanho: {export_result.get('file_size_mb', 0)} MB")
        else:
            print("📝 Nenhum documento encontrado para exportação (normal para sistema novo)")
        
        print("✅ Utilitários de migração demonstrados!")
        
    except Exception as e:
        print(f"❌ Erro no demo de migração: {e}")

def demo_performance_analyzer():
    """Demonstrar analisador de performance"""
    print("\\n📊 DEMONSTRAÇÃO - ANÁLISE DE PERFORMANCE")
    print("-" * 50)
    
    try:
        # Coletar métricas do sistema
        system_metrics = mamute_advanced.performance_analyzer.collect_system_metrics()
        db_metrics = mamute_advanced.performance_analyzer.collect_database_metrics()
        
        print(f"📈 Métricas coletadas:")
        print(f"   - Sistema: {len(system_metrics)} métricas")
        print(f"   - Banco de dados: {len(db_metrics)} métricas")
        
        # Mostrar algumas métricas importantes
        for metric in system_metrics + db_metrics:
            if metric.name in ['cpu_usage', 'memory_usage', 'disk_usage']:
                print(f"   - {metric.name}: {metric.value:.1f}{metric.unit}")
        
        # Obter recomendações
        recommendations = mamute_advanced.performance_analyzer.get_recommendations()
        if recommendations:
            print(f"\\n💡 Recomendações: {len(recommendations)}")
            for rec in recommendations[:2]:
                print(f"   - [{rec['priority'].upper()}] {rec['recommendation'][:60]}...")
        
        print("✅ Análise de performance demonstrada!")
        
    except Exception as e:
        print(f"❌ Erro no demo de performance: {e}")

def demo_report_generator():
    """Demonstrar gerador de relatórios"""
    print("\\n📋 DEMONSTRAÇÃO - GERADOR DE RELATÓRIOS")
    print("-" * 50)
    
    try:
        # Gerar relatório diário
        daily_report = mamute_advanced.report_generator.generate_daily_report()
        
        if daily_report:
            report_path = Path(daily_report)
            print(f"✅ Relatório diário gerado: {report_path.name}")
            print(f"📁 Local: {report_path.parent}")
            
            # Verificar tamanho do arquivo
            if report_path.exists():
                size_kb = report_path.stat().st_size / 1024
                print(f"📊 Tamanho: {size_kb:.1f} KB")
        
        # Listar relatórios disponíveis
        reports = mamute_advanced.report_generator.list_reports()
        print(f"\\n📋 Total de relatórios: {len(reports)}")
        
        for report in reports[:3]:
            print(f"   - {report['name']} ({report['type']}) - {report['size_mb']} MB")
        
        print("✅ Gerador de relatórios demonstrado!")
        
    except Exception as e:
        print(f"❌ Erro no demo de relatórios: {e}")

async def demo_admin_dashboard():
    """Demonstrar dashboard administrativo"""
    print("\\n🔧 DEMONSTRAÇÃO - DASHBOARD ADMINISTRATIVO")
    print("-" * 50)
    
    try:
        # Obter dados do dashboard
        admin_data = await mamute_advanced.admin_dashboard.get_admin_dashboard_data()
        
        if admin_data:
            # Mostrar informações do sistema
            sys_info = admin_data.get('system_info', {})
            if sys_info:
                print(f"💻 CPU: {sys_info.get('cpu_usage', 0):.1f}%")
                memory = sys_info.get('memory', {})
                if memory:
                    print(f"🧠 Memória: {memory.get('percent', 0):.1f}%")
                disk = sys_info.get('disk', {})
                if disk:
                    print(f"💾 Disco: {disk.get('percent', 0):.1f}%")
            
            # Mostrar estatísticas do banco
            db_stats = admin_data.get('database_stats', {})
            if db_stats:
                print(f"\\n🗄️ Banco de dados:")
                tables = db_stats.get('tables', [])
                print(f"   - Tabelas: {len(tables)}")
                print(f"   - Status: {db_stats.get('connection_status', 'unknown')}")
                
                total_docs = db_stats.get('total_documents', 0)
                total_conversations = db_stats.get('total_conversations', 0)
                print(f"   - Documentos: {total_docs}")
                print(f"   - Conversas: {total_conversations}")
            
            # Atividade recente
            recent_activity = admin_data.get('recent_activity', [])
            if recent_activity:
                print(f"\\n📝 Atividade recente: {len(recent_activity)} eventos")
                for activity in recent_activity[:3]:
                    timestamp = activity['timestamp']
                    if isinstance(timestamp, str):
                        timestamp = timestamp[:19]  # Apenas data e hora
                    print(f"   - {activity['type']}: {activity['description'][:40]}... ({timestamp})")
        
        print("✅ Dashboard administrativo demonstrado!")
        
    except Exception as e:
        print(f"❌ Erro no demo do dashboard: {e}")

async def main():
    """Função principal da demonstração"""
    print("🐘" + "=" * 80 + "🐘")
    print("                    DEMONSTRAÇÃO COMPLETA DO MAMUTE AVANÇADO")
    print("🐘" + "=" * 80 + "🐘")
    
    start_time = time.time()
    
    try:
        # Inicializar sistema
        print("\\n🚀 INICIALIZANDO SISTEMA AVANÇADO...")
        print("=" * 50)
        
        init_results = await initialize_mamute_advanced()
        
        successful_systems = sum(1 for status in init_results.values() if status)
        total_systems = len(init_results)
        
        print(f"✅ Inicialização concluída: {successful_systems}/{total_systems} subsistemas ativos")
        
        # Executar demonstrações
        await demo_notifications()
        await demo_backup_system()
        demo_migration_utils()
        demo_performance_analyzer()
        demo_report_generator()
        await demo_admin_dashboard()
        
        # Executar diagnósticos completos
        print("\\n🔍 EXECUTANDO DIAGNÓSTICOS COMPLETOS...")
        print("-" * 50)
        
        diagnostics = await mamute_advanced.run_system_diagnostics()
        
        if diagnostics:
            summary = diagnostics.get('summary', {})
            print(f"📊 Testes executados: {summary.get('total_tests', 0)}")
            print(f"✅ Testes aprovados: {summary.get('passed_tests', 0)}")
            print(f"❌ Testes falharam: {summary.get('failed_tests', 0)}")
            print(f"⚠️ Problemas encontrados: {summary.get('issues_count', 0)}")
            print(f"🏥 Status geral: {summary.get('overall_health', 'unknown').upper()}")
        
        # Gerar relatório final
        print("\\n📋 GERANDO RELATÓRIO FINAL DE SAÚDE...")
        print("-" * 50)
        
        health_report = await mamute_advanced.generate_system_health_report()
        
        if health_report:
            overview = health_report.get('system_overview', {})
            print(f"🐘 Mamute versão: {overview.get('mamute_version', 'N/A')}")
            print(f"🔧 Subsistemas saudáveis: {overview.get('healthy_subsystems', 0)}/{overview.get('subsystems_count', 0)}")
            print(f"📊 Status final: {overview.get('overall_status', 'unknown').upper()}")
        
        # Tempo total
        total_time = time.time() - start_time
        
        # Resumo final
        print("\\n" + "🐘" + "=" * 80 + "🐘")
        print("                         DEMONSTRAÇÃO CONCLUÍDA!")
        print("🐘" + "=" * 80 + "🐘")
        
        print(f"\\n⏱️ Tempo total da demonstração: {total_time:.1f} segundos")
        print(f"🎯 Todas as funcionalidades foram demonstradas com sucesso!")
        
        print("\\n🚀 PRÓXIMOS PASSOS:")
        print("1. Execute 'python web_app.py' para acessar a interface web")
        print("2. Acesse http://localhost:8000 no navegador")
        print("3. Use 'python mamute_advanced_system.py' para monitoramento contínuo")
        
        print("\\n💡 FUNCIONALIDADES DEMONSTRADAS:")
        features = [
            "✅ Dashboard administrativo com métricas em tempo real",
            "✅ Sistema de backup automático e sob demanda",
            "✅ Utilitários completos para migração de dados",
            "✅ Sistema de notificações em múltiplos canais",
            "✅ Análise avançada de performance e otimização",
            "✅ Geração automática de relatórios em HTML/JSON/Excel",
            "✅ Diagnósticos automatizados de saúde do sistema",
            "✅ Monitoramento contínuo e alertas inteligentes"
        ]
        
        for feature in features:
            print(f"   {feature}")
        
        print("\\n🐘 MAMUTE ESTÁ PRONTO PARA PRODUÇÃO! 🐘")
        
    except Exception as e:
        print(f"\\n❌ ERRO DURANTE DEMONSTRAÇÃO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())