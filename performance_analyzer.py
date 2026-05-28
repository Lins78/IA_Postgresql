"""
Análises de Performance Avançadas do Mamute
Sistema para monitoramento detalhado e otimização automática
"""
import os
import sys
import time
import asyncio
import statistics
from datetime import datetime, timedelta
from pathlib import Path

# Tentar importar psutil, usar fallback se não disponível
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
from collections import defaultdict, deque
import threading

# Adicionar o diretório principal ao path
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
APPS_DIR = SRC_DIR / "apps"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(APPS_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_DIR))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.database.connection import DatabaseManager

@dataclass
class PerformanceMetric:
    """Estrutura para métrica de performance"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    category: str
    metadata: Dict[str, Any] = None

@dataclass
class QueryAnalysis:
    """Análise de consulta SQL"""
    query_id: str
    query_text: str
    execution_time: float
    rows_returned: int
    memory_usage: float
    cpu_usage: float
    timestamp: datetime
    optimizable: bool = False
    suggestions: List[str] = None

class PerformanceAnalyzer:
    """Analisador de performance avançado do Mamute"""
    
    def __init__(self, config_file: str = ".env"):
        """Inicializar analisador de performance"""
        self.config = Config(config_file)
        self.logger = setup_logger("PerformanceAnalyzer")
        self.db_manager = DatabaseManager(self.config)
        
        # Métricas em tempo real
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.query_history = deque(maxlen=500)
        
        # Configurações de análise
        self.analysis_interval = 30  # segundos
        self.slow_query_threshold = 1.0  # segundos
        self.memory_warning_threshold = 80  # porcentagem
        self.cpu_warning_threshold = 90  # porcentagem
        
        # Monitoramento ativo
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Cache de análises
        self.cached_analyses = {}
        self.cache_ttl = 300  # 5 minutos
        
        # Configurar extensões do PostgreSQL para análise
        self._setup_pg_extensions()
        
        self.logger.info("Analisador de performance avançado inicializado")
    
    def _setup_pg_extensions(self):
        """Configurar extensões necessárias do PostgreSQL"""
        try:
            # Tentar habilitar pg_stat_statements para análise de queries
            self.db_manager.execute_query("CREATE EXTENSION IF NOT EXISTS pg_stat_statements")
            self.logger.info("Extensão pg_stat_statements habilitada")
        except Exception as e:
            self.logger.warning(f"Não foi possível habilitar pg_stat_statements: {e}")
        
        try:
            # Habilitar pg_buffercache para análise de cache
            self.db_manager.execute_query("CREATE EXTENSION IF NOT EXISTS pg_buffercache")
            self.logger.debug("Extensão pg_buffercache habilitada")
        except Exception as e:
            self.logger.warning(f"Não foi possível habilitar pg_buffercache: {e}")
    
    def collect_system_metrics(self) -> List[PerformanceMetric]:
        """Coletar métricas do sistema"""
        timestamp = datetime.now()
        metrics = []
        
        try:
            if not PSUTIL_AVAILABLE:
                self.logger.warning("psutil não disponível - métricas de sistema limitadas")
                return [PerformanceMetric(
                    "system_status", 0, "status", timestamp, "system",
                    {"warning": "psutil não disponível - instale com: pip install psutil"}
                )]
            
            # Métricas de CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            metrics.extend([
                PerformanceMetric("cpu_usage", cpu_percent, "%", timestamp, "system"),
                PerformanceMetric("cpu_count", cpu_count, "cores", timestamp, "system"),
                PerformanceMetric("cpu_frequency", cpu_freq.current if cpu_freq else 0, "MHz", timestamp, "system")
            ])
            
            # Métricas de memória
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            metrics.extend([
                PerformanceMetric("memory_usage", memory.percent, "%", timestamp, "memory"),
                PerformanceMetric("memory_available", memory.available / (1024**3), "GB", timestamp, "memory"),
                PerformanceMetric("memory_total", memory.total / (1024**3), "GB", timestamp, "memory"),
                PerformanceMetric("swap_usage", swap.percent, "%", timestamp, "memory")
            ])
            
            # Métricas de disco
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            metrics.extend([
                PerformanceMetric("disk_usage", (disk.used / disk.total) * 100, "%", timestamp, "storage"),
                PerformanceMetric("disk_free", disk.free / (1024**3), "GB", timestamp, "storage"),
                PerformanceMetric("disk_read_bytes", disk_io.read_bytes if disk_io else 0, "bytes", timestamp, "storage"),
                PerformanceMetric("disk_write_bytes", disk_io.write_bytes if disk_io else 0, "bytes", timestamp, "storage")
            ])
            
            # Métricas de rede
            network = psutil.net_io_counters()
            if network:
                metrics.extend([
                    PerformanceMetric("network_bytes_sent", network.bytes_sent, "bytes", timestamp, "network"),
                    PerformanceMetric("network_bytes_recv", network.bytes_recv, "bytes", timestamp, "network"),
                    PerformanceMetric("network_packets_sent", network.packets_sent, "packets", timestamp, "network"),
                    PerformanceMetric("network_packets_recv", network.packets_recv, "packets", timestamp, "network")
                ])
            
            # Adicionar ao histórico
            for metric in metrics:
                self.metrics_history[metric.name].append((metric.timestamp, metric.value))
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas do sistema: {e}")
            return []
    
    def collect_database_metrics(self) -> List[PerformanceMetric]:
        """Coletar métricas específicas do PostgreSQL"""
        timestamp = datetime.now()
        metrics = []
        
        try:
            # Estatísticas de conexão
            connections = self.db_manager.execute_query("""
                SELECT 
                    COUNT(*) as total_connections,
                    COUNT(*) FILTER (WHERE state = 'active') as active_connections,
                    COUNT(*) FILTER (WHERE state = 'idle') as idle_connections
                FROM pg_stat_activity
                WHERE pid <> pg_backend_pid()
            """)
            
            if connections:
                conn_data = connections[0]
                metrics.extend([
                    PerformanceMetric("db_total_connections", conn_data['total_connections'], "connections", timestamp, "database"),
                    PerformanceMetric("db_active_connections", conn_data['active_connections'], "connections", timestamp, "database"),
                    PerformanceMetric("db_idle_connections", conn_data['idle_connections'], "connections", timestamp, "database")
                ])
            
            # Cache hit ratio
            cache_stats = self.db_manager.execute_query("""
                SELECT 
                    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) * 100 as cache_hit_ratio,
                    sum(heap_blks_read) as blocks_read,
                    sum(heap_blks_hit) as blocks_hit
                FROM pg_statio_user_tables
            """)
            
            if cache_stats and cache_stats[0]['cache_hit_ratio']:
                cache_data = cache_stats[0]
                metrics.extend([
                    PerformanceMetric("db_cache_hit_ratio", float(cache_data['cache_hit_ratio']), "%", timestamp, "database"),
                    PerformanceMetric("db_blocks_read", cache_data['blocks_read'], "blocks", timestamp, "database"),
                    PerformanceMetric("db_blocks_hit", cache_data['blocks_hit'], "blocks", timestamp, "database")
                ])
            
            # Tamanho do banco
            db_size = self.db_manager.execute_query("""
                SELECT pg_database_size(current_database()) as size_bytes
            """)
            
            if db_size:
                size_gb = db_size[0]['size_bytes'] / (1024**3)
                metrics.append(PerformanceMetric("db_size", size_gb, "GB", timestamp, "database"))
            
            # Estatísticas de transações
            tx_stats = self.db_manager.execute_query("""
                SELECT 
                    xact_commit,
                    xact_rollback,
                    blks_read,
                    blks_hit,
                    tup_returned,
                    tup_fetched,
                    tup_inserted,
                    tup_updated,
                    tup_deleted
                FROM pg_stat_database 
                WHERE datname = current_database()
            """)
            
            if tx_stats:
                tx_data = tx_stats[0]
                metrics.extend([
                    PerformanceMetric("db_commits", tx_data['xact_commit'], "transactions", timestamp, "database"),
                    PerformanceMetric("db_rollbacks", tx_data['xact_rollback'], "transactions", timestamp, "database"),
                    PerformanceMetric("db_tuples_returned", tx_data['tup_returned'], "tuples", timestamp, "database"),
                    PerformanceMetric("db_tuples_fetched", tx_data['tup_fetched'], "tuples", timestamp, "database")
                ])
            
            # Adicionar ao histórico
            for metric in metrics:
                self.metrics_history[metric.name].append((metric.timestamp, metric.value))
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas do banco: {e}")
            return []
    
    def analyze_slow_queries(self, limit: int = 10) -> List[QueryAnalysis]:
        """Analisar consultas lentas"""
        try:
            slow_queries = self.db_manager.execute_query("""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    max_time,
                    stddev_time,
                    rows,
                    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                FROM pg_stat_statements 
                WHERE mean_time > %(threshold)s
                ORDER BY total_time DESC 
                LIMIT %(limit)s
            """, {'threshold': self.slow_query_threshold * 1000, 'limit': limit})  # pg_stat_statements usa ms
            
            analyses = []
            
            for query_data in slow_queries or []:
                # Gerar sugestões de otimização
                suggestions = []
                
                # Verificar cache hit ratio
                hit_percent = query_data.get('hit_percent', 0) or 0
                if hit_percent < 95:
                    suggestions.append("Considere adicionar índices para melhorar cache hit ratio")
                
                # Verificar tempo médio
                if query_data['mean_time'] > 5000:  # 5 segundos
                    suggestions.append("Query muito lenta - considere otimização ou particionamento")
                
                # Verificar número de linhas retornadas
                if query_data['rows'] > 10000:
                    suggestions.append("Muitas linhas retornadas - considere paginação ou filtros")
                
                # Verificar desvio padrão
                if query_data.get('stddev_time', 0) > query_data['mean_time']:
                    suggestions.append("Tempo de execução inconsistente - verifique variações na carga")
                
                analysis = QueryAnalysis(
                    query_id=f"slow_{hash(query_data['query']) % 10000}",
                    query_text=query_data['query'][:200] + "..." if len(query_data['query']) > 200 else query_data['query'],
                    execution_time=query_data['mean_time'] / 1000,  # converter para segundos
                    rows_returned=query_data['rows'],
                    memory_usage=0,  # Não disponível em pg_stat_statements
                    cpu_usage=0,     # Não disponível em pg_stat_statements
                    timestamp=datetime.now(),
                    optimizable=len(suggestions) > 0,
                    suggestions=suggestions
                )
                
                analyses.append(analysis)
                
                # Adicionar ao histórico
                self.query_history.append(analysis)
            
            return analyses
            
        except Exception as e:
            self.logger.warning(f"Erro ao analisar consultas lentas: {e}")
            return []
    
    def analyze_table_performance(self) -> Dict[str, Any]:
        """Analisar performance das tabelas"""
        try:
            # Estatísticas detalhadas das tabelas
            table_stats = self.db_manager.execute_query("""
                SELECT 
                    schemaname,
                    tablename,
                    seq_scan,
                    seq_tup_read,
                    idx_scan,
                    idx_tup_fetch,
                    n_tup_ins,
                    n_tup_upd,
                    n_tup_del,
                    n_live_tup,
                    n_dead_tup,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables
                ORDER BY seq_tup_read DESC
            """)
            
            # Tamanhos das tabelas
            table_sizes = self.db_manager.execute_query("""
                SELECT 
                    schemaname,
                    tablename,
                    pg_total_relation_size(schemaname||'.'||tablename) as total_size,
                    pg_relation_size(schemaname||'.'||tablename) as table_size,
                    pg_indexes_size(schemaname||'.'||tablename) as indexes_size
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """)
            
            # Análise de índices
            index_usage = self.db_manager.execute_query("""
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_tup_read,
                    idx_tup_fetch,
                    pg_relation_size(indexrelid) as index_size
                FROM pg_stat_user_indexes 
                ORDER BY idx_tup_read DESC
            """)
            
            # Consolidar análise
            analysis = {
                'table_statistics': table_stats or [],
                'table_sizes': table_sizes or [],
                'index_usage': index_usage or [],
                'recommendations': []
            }
            
            # Gerar recomendações
            for table in table_stats or []:
                table_name = table['tablename']
                
                # Verificar ratio seq_scan vs idx_scan
                seq_scans = table.get('seq_scan', 0) or 0
                idx_scans = table.get('idx_scan', 0) or 0
                
                if seq_scans > idx_scans and seq_scans > 100:
                    analysis['recommendations'].append({
                        'type': 'index_needed',
                        'table': table_name,
                        'message': f'Tabela {table_name} tem muitos sequential scans - considere adicionar índices'
                    })
                
                # Verificar dead tuples
                dead_tup = table.get('n_dead_tup', 0) or 0
                live_tup = table.get('n_live_tup', 0) or 0
                
                if dead_tup > live_tup * 0.1 and dead_tup > 1000:
                    analysis['recommendations'].append({
                        'type': 'vacuum_needed',
                        'table': table_name,
                        'message': f'Tabela {table_name} tem muitas dead tuples - execute VACUUM'
                    })
                
                # Verificar última análise
                last_analyze = table.get('last_analyze') or table.get('last_autoanalyze')
                if not last_analyze or (datetime.now() - last_analyze).days > 7:
                    analysis['recommendations'].append({
                        'type': 'analyze_needed',
                        'table': table_name,
                        'message': f'Tabela {table_name} precisa de ANALYZE para estatísticas atualizadas'
                    })
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar performance das tabelas: {e}")
            return {}
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Gerar relatório completo de performance"""
        try:
            timestamp = datetime.now()
            
            # Coletar todas as métricas
            system_metrics = self.collect_system_metrics()
            db_metrics = self.collect_database_metrics()
            slow_queries = self.analyze_slow_queries()
            table_analysis = self.analyze_table_performance()
            
            # Análise de tendências (últimos 10 pontos de dados)
            trends = {}
            for metric_name, history in self.metrics_history.items():
                if len(history) >= 5:
                    recent_values = [point[1] for point in list(history)[-10:]]
                    trends[metric_name] = {
                        'current': recent_values[-1],
                        'average': statistics.mean(recent_values),
                        'trend': 'increasing' if recent_values[-1] > statistics.mean(recent_values) else 'decreasing',
                        'volatility': statistics.stdev(recent_values) if len(recent_values) > 1 else 0
                    }
            
            # Alertas críticos
            alerts = []
            
            # Verificar métricas críticas
            for metric in system_metrics + db_metrics:
                if metric.name == "memory_usage" and metric.value > self.memory_warning_threshold:
                    alerts.append({
                        'level': 'warning',
                        'type': 'memory',
                        'message': f'Uso de memória alto: {metric.value:.1f}%'
                    })
                
                if metric.name == "cpu_usage" and metric.value > self.cpu_warning_threshold:
                    alerts.append({
                        'level': 'critical',
                        'type': 'cpu',
                        'message': f'Uso de CPU crítico: {metric.value:.1f}%'
                    })
                
                if metric.name == "disk_usage" and metric.value > 85:
                    alerts.append({
                        'level': 'warning',
                        'type': 'storage',
                        'message': f'Uso de disco alto: {metric.value:.1f}%'
                    })
                
                if metric.name == "db_cache_hit_ratio" and metric.value < 95:
                    alerts.append({
                        'level': 'warning',
                        'type': 'database',
                        'message': f'Cache hit ratio baixo: {metric.value:.1f}%'
                    })
            
            # Verificar consultas lentas
            if len(slow_queries) > 5:
                alerts.append({
                    'level': 'warning',
                    'type': 'performance',
                    'message': f'Detectadas {len(slow_queries)} consultas lentas'
                })
            
            report = {
                'timestamp': timestamp.isoformat(),
                'system_metrics': [
                    {
                        'name': m.name,
                        'value': m.value,
                        'unit': m.unit,
                        'category': m.category,
                        'timestamp': m.timestamp.isoformat()
                    }
                    for m in system_metrics
                ],
                'database_metrics': [
                    {
                        'name': m.name,
                        'value': m.value,
                        'unit': m.unit,
                        'category': m.category,
                        'timestamp': m.timestamp.isoformat()
                    }
                    for m in db_metrics
                ],
                'slow_queries': [
                    {
                        'query_id': q.query_id,
                        'query_text': q.query_text,
                        'execution_time': q.execution_time,
                        'rows_returned': q.rows_returned,
                        'optimizable': q.optimizable,
                        'suggestions': q.suggestions or []
                    }
                    for q in slow_queries
                ],
                'table_analysis': table_analysis,
                'trends': trends,
                'alerts': alerts,
                'summary': {
                    'total_metrics_collected': len(system_metrics) + len(db_metrics),
                    'slow_queries_detected': len(slow_queries),
                    'critical_alerts': len([a for a in alerts if a['level'] == 'critical']),
                    'warning_alerts': len([a for a in alerts if a['level'] == 'warning']),
                    'overall_health': 'critical' if any(a['level'] == 'critical' for a in alerts) 
                                   else 'warning' if alerts 
                                   else 'healthy'
                }
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório de performance: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def start_monitoring(self):
        """Iniciar monitoramento contínuo"""
        if self.monitoring_active:
            self.logger.warning("Monitoramento já está ativo")
            return
        
        self.monitoring_active = True
        
        def monitor_loop():
            """Loop de monitoramento"""
            self.logger.info("Monitoramento de performance iniciado")
            
            while self.monitoring_active:
                try:
                    # Coletar métricas
                    self.collect_system_metrics()
                    self.collect_database_metrics()
                    
                    # Verificar alertas críticos
                    report = self.generate_performance_report()
                    critical_alerts = [a for a in report.get('alerts', []) if a['level'] == 'critical']
                    
                    if critical_alerts:
                        for alert in critical_alerts:
                            self.logger.critical(f"ALERTA CRÍTICO: {alert['message']}")
                    
                    # Aguardar próximo ciclo
                    time.sleep(self.analysis_interval)
                    
                except Exception as e:
                    self.logger.error(f"Erro no loop de monitoramento: {e}")
                    time.sleep(self.analysis_interval)
            
            self.logger.info("Monitoramento de performance interrompido")
        
        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Parar monitoramento contínuo"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Monitoramento de performance parado")
    
    def get_recommendations(self) -> List[Dict[str, str]]:
        """Obter recomendações de otimização"""
        try:
            recommendations = []
            
            # Análise baseada no histórico de métricas
            if 'memory_usage' in self.metrics_history:
                memory_history = [point[1] for point in self.metrics_history['memory_usage']]
                if len(memory_history) >= 5:
                    avg_memory = statistics.mean(memory_history[-10:])
                    if avg_memory > 80:
                        recommendations.append({
                            'type': 'memory_optimization',
                            'priority': 'high',
                            'recommendation': 'Considere aumentar a memória RAM ou otimizar consultas que consomem muita memória'
                        })
            
            # Análise de cache hit ratio
            if 'db_cache_hit_ratio' in self.metrics_history:
                cache_history = [point[1] for point in self.metrics_history['db_cache_hit_ratio']]
                if len(cache_history) >= 5:
                    avg_cache = statistics.mean(cache_history[-10:])
                    if avg_cache < 95:
                        recommendations.append({
                            'type': 'cache_optimization',
                            'priority': 'medium',
                            'recommendation': 'Cache hit ratio baixo - considere aumentar shared_buffers no PostgreSQL'
                        })
            
            # Recomendações baseadas em consultas lentas
            slow_query_count = len([q for q in self.query_history if q.execution_time > self.slow_query_threshold])
            if slow_query_count > 10:
                recommendations.append({
                    'type': 'query_optimization',
                    'priority': 'high',
                    'recommendation': f'Detectadas {slow_query_count} consultas lentas - revisar e otimizar queries'
                })
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar recomendações: {e}")
            return []

# Instância global do analisador
performance_analyzer = PerformanceAnalyzer()

def main():
    """Função principal para demonstrar análises de performance"""
    print("🐘 ANÁLISES DE PERFORMANCE AVANÇADAS DO MAMUTE")
    print("=" * 60)
    
    try:
        # Gerar relatório de performance
        print("\\n📊 Gerando relatório de performance...")
        report = performance_analyzer.generate_performance_report()
        
        print(f"✅ Relatório gerado: {report['timestamp']}")
        print(f"📈 Métricas coletadas: {report['summary']['total_metrics_collected']}")
        print(f"🐌 Consultas lentas: {report['summary']['slow_queries_detected']}")
        print(f"⚠️ Alertas: {report['summary']['warning_alerts']} warnings, {report['summary']['critical_alerts']} críticos")
        print(f"🏥 Status geral: {report['summary']['overall_health'].upper()}")
        
        # Mostrar alertas se houver
        if report['alerts']:
            print("\\n🚨 ALERTAS:")
            for alert in report['alerts'][:5]:  # Mostrar apenas os 5 primeiros
                emoji = "🚨" if alert['level'] == 'critical' else "⚠️"
                print(f"   {emoji} [{alert['type'].upper()}] {alert['message']}")
        
        # Mostrar recomendações
        recommendations = performance_analyzer.get_recommendations()
        if recommendations:
            print("\\n💡 RECOMENDAÇÕES:")
            for rec in recommendations[:3]:  # Mostrar apenas as 3 primeiras
                priority_emoji = "🔥" if rec['priority'] == 'high' else "🔸"
                print(f"   {priority_emoji} {rec['recommendation']}")
        
        print("\\n✅ Sistema de análise de performance configurado!")
        print("💡 Use performance_analyzer.start_monitoring() para monitoramento contínuo")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()