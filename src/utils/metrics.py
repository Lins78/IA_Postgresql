"""
Sistema de Métricas Avançadas para Dashboard Mamute
"""
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
from collections import defaultdict

from ..database.connection import DatabaseManager
from ..utils.config import Config
from ..utils.logger import setup_logger

class AdvancedMetricsManager:
    """Gerenciador de métricas avançadas para o dashboard"""
    
    def __init__(self, db_manager: DatabaseManager, config: Config):
        self.db_manager = db_manager
        self.config = config
        self.logger = setup_logger(__name__, config.log_level)
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos
        
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Coleta todas as métricas para o dashboard"""
        try:
            return {
                'system_health': self._get_system_health(),
                'database_stats': self._get_database_stats(),
                'performance_metrics': self._get_performance_metrics(),
                'recent_activity': self._get_recent_activity(),
                'storage_analysis': self._get_storage_analysis(),
                'query_analytics': self._get_query_analytics(),
                'connection_stats': self._get_connection_stats(),
                'error_monitoring': self._get_error_monitoring()
            }
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas: {e}")
            return self._get_fallback_metrics()
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Status geral do sistema"""
        try:
            # Verificar conexão DB
            db_status = self.db_manager.test_connection()
            
            # Métricas de sistema
            uptime = self._calculate_uptime()
            
            return {
                'status': 'healthy' if db_status else 'warning',
                'database_connected': db_status,
                'uptime': uptime,
                'timestamp': datetime.now().isoformat(),
                'version': self.config.app_version if hasattr(self.config, 'app_version') else '1.0.0'
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _get_database_stats(self) -> Dict[str, Any]:
        """Estatísticas gerais do banco de dados"""
        cache_key = 'database_stats'
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            # Tamanho do banco
            size_query = "SELECT pg_size_pretty(pg_database_size(current_database())) as size"
            size_result = self.db_manager.execute_query(size_query)
            
            # Número de tabelas
            tables_query = """
                SELECT COUNT(*) as table_count 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """
            tables_result = self.db_manager.execute_query(tables_query)
            
            # Número total de registros (estimativa)
            records_query = """
                SELECT SUM(n_tup_ins + n_tup_upd) as total_operations,
                       SUM(n_tup_del) as total_deletions,
                       SUM(seq_scan) as sequential_scans,
                       SUM(idx_scan) as index_scans
                FROM pg_stat_user_tables
            """
            stats_result = self.db_manager.execute_query(records_query)
            
            result = {
                'database_size': size_result[0]['size'] if size_result else 'N/A',
                'table_count': tables_result[0]['table_count'] if tables_result else 0,
                'total_operations': int(stats_result[0]['total_operations'] or 0) if stats_result else 0,
                'total_deletions': int(stats_result[0]['total_deletions'] or 0) if stats_result else 0,
                'sequential_scans': int(stats_result[0]['sequential_scans'] or 0) if stats_result else 0,
                'index_scans': int(stats_result[0]['index_scans'] or 0) if stats_result else 0,
                'timestamp': datetime.now().isoformat()
            }
            
            self._cache_result(cache_key, result)
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar stats do banco: {e}")
            return {
                'database_size': 'Erro',
                'table_count': 0,
                'error': str(e)
            }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Métricas de performance"""
        try:
            # Consultas mais lentas (se pg_stat_statements estiver habilitado)
            slow_queries = self._get_slow_queries()
            
            # Índices não utilizados
            unused_indexes = self._get_unused_indexes()
            
            # Tabelas que necessitam VACUUM
            vacuum_needed = self._get_vacuum_candidates()
            
            # Hit ratio do cache
            cache_hit_ratio = self._get_cache_hit_ratio()
            
            return {
                'slow_queries': slow_queries,
                'unused_indexes': unused_indexes,
                'vacuum_candidates': vacuum_needed,
                'cache_hit_ratio': cache_hit_ratio,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_recent_activity(self) -> Dict[str, Any]:
        """Atividade recente no sistema"""
        try:
            # Atividade de conexões
            connections_query = """
                SELECT state, COUNT(*) as count
                FROM pg_stat_activity 
                WHERE pid <> pg_backend_pid()
                GROUP BY state
            """
            
            connections = self.db_manager.execute_query(connections_query)
            
            # Últimas consultas (se disponível)
            recent_queries = self._get_recent_queries()
            
            return {
                'active_connections': connections,
                'recent_queries': recent_queries,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_storage_analysis(self) -> Dict[str, Any]:
        """Análise de armazenamento"""
        try:
            # Top 10 tabelas por tamanho
            size_query = """
                SELECT 
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 10
            """
            
            table_sizes = self.db_manager.execute_query(size_query)
            
            # Distribuição de tipos de dados
            column_types_query = """
                SELECT data_type, COUNT(*) as count
                FROM information_schema.columns 
                WHERE table_schema = 'public'
                GROUP BY data_type
                ORDER BY count DESC
            """
            
            column_types = self.db_manager.execute_query(column_types_query)
            
            return {
                'largest_tables': table_sizes,
                'column_type_distribution': column_types,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_query_analytics(self) -> Dict[str, Any]:
        """Análise de consultas"""
        try:
            # Estatísticas de tabelas
            table_stats_query = """
                SELECT 
                    schemaname,
                    tablename,
                    seq_scan as sequential_scans,
                    seq_tup_read as rows_read_sequentially,
                    idx_scan as index_scans,
                    idx_tup_fetch as rows_fetched_via_index,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes
                FROM pg_stat_user_tables
                ORDER BY (seq_scan + idx_scan) DESC
                LIMIT 10
            """
            
            table_stats = self.db_manager.execute_query(table_stats_query)
            
            return {
                'table_activity': table_stats,
                'scan_ratio_warning': self._analyze_scan_ratios(table_stats),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_connection_stats(self) -> Dict[str, Any]:
        """Estatísticas de conexões"""
        try:
            # Conexões por estado
            conn_query = """
                SELECT 
                    state,
                    COUNT(*) as count,
                    MAX(EXTRACT(EPOCH FROM (now() - state_change))) as max_duration
                FROM pg_stat_activity 
                WHERE pid <> pg_backend_pid()
                GROUP BY state
            """
            
            connections = self.db_manager.execute_query(conn_query)
            
            # Conexões por database
            db_conn_query = """
                SELECT 
                    datname,
                    COUNT(*) as connections
                FROM pg_stat_activity 
                WHERE pid <> pg_backend_pid()
                GROUP BY datname
            """
            
            db_connections = self.db_manager.execute_query(db_conn_query)
            
            return {
                'by_state': connections,
                'by_database': db_connections,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_error_monitoring(self) -> Dict[str, Any]:
        """Monitoramento de erros"""
        try:
            # Verificar deadlocks
            deadlocks_query = "SELECT deadlocks FROM pg_stat_database WHERE datname = current_database()"
            deadlocks = self.db_manager.execute_query(deadlocks_query)
            
            # Verificar conflitos
            conflicts_query = "SELECT conflicts FROM pg_stat_database WHERE datname = current_database()"
            conflicts = self.db_manager.execute_query(conflicts_query)
            
            return {
                'deadlocks': deadlocks[0]['deadlocks'] if deadlocks else 0,
                'conflicts': conflicts[0]['conflicts'] if conflicts else 0,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    # Métodos auxiliares
    def _get_slow_queries(self) -> List[Dict]:
        """Busca consultas lentas (requer pg_stat_statements)"""
        try:
            query = """
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows
                FROM pg_stat_statements 
                ORDER BY mean_time DESC 
                LIMIT 5
            """
            return self.db_manager.execute_query(query)
        except:
            return []
    
    def _get_unused_indexes(self) -> List[Dict]:
        """Índices não utilizados"""
        try:
            query = """
                SELECT 
                    indexrelname as index_name,
                    tablename,
                    idx_scan as scans
                FROM pg_stat_user_indexes 
                WHERE idx_scan = 0
            """
            return self.db_manager.execute_query(query)
        except:
            return []
    
    def _get_vacuum_candidates(self) -> List[Dict]:
        """Tabelas que necessitam VACUUM"""
        try:
            query = """
                SELECT 
                    tablename,
                    n_dead_tup as dead_tuples,
                    n_live_tup as live_tuples,
                    ROUND(n_dead_tup * 100.0 / GREATEST(n_live_tup, 1), 2) as dead_ratio
                FROM pg_stat_user_tables 
                WHERE n_dead_tup > 100
                ORDER BY dead_ratio DESC
            """
            return self.db_manager.execute_query(query)
        except:
            return []
    
    def _get_cache_hit_ratio(self) -> float:
        """Taxa de acerto do cache"""
        try:
            query = """
                SELECT 
                    ROUND(
                        (blks_hit * 100.0) / GREATEST(blks_hit + blks_read, 1), 2
                    ) as cache_hit_ratio
                FROM pg_stat_database 
                WHERE datname = current_database()
            """
            result = self.db_manager.execute_query(query)
            return float(result[0]['cache_hit_ratio']) if result else 0.0
        except:
            return 0.0
    
    def _get_recent_queries(self) -> List[Dict]:
        """Consultas recentes"""
        try:
            query = """
                SELECT 
                    query,
                    state,
                    EXTRACT(EPOCH FROM (now() - query_start)) as duration
                FROM pg_stat_activity 
                WHERE query != '<IDLE>'
                  AND pid <> pg_backend_pid()
                ORDER BY query_start DESC 
                LIMIT 5
            """
            return self.db_manager.execute_query(query)
        except:
            return []
    
    def _analyze_scan_ratios(self, table_stats: List[Dict]) -> List[Dict]:
        """Analisa ratios de scan para identificar problemas"""
        warnings = []
        
        for table in table_stats:
            seq_scans = table.get('sequential_scans', 0) or 0
            idx_scans = table.get('index_scans', 0) or 0
            
            if seq_scans > 0 and idx_scans > 0:
                ratio = seq_scans / (seq_scans + idx_scans)
                if ratio > 0.7:  # Mais de 70% sequential scans
                    warnings.append({
                        'table': table['tablename'],
                        'issue': 'Alto uso de sequential scans',
                        'ratio': round(ratio * 100, 2),
                        'recommendation': f'Considere criar índices para a tabela {table["tablename"]}'
                    })
        
        return warnings
    
    def _calculate_uptime(self) -> str:
        """Calcula uptime do sistema"""
        try:
            query = "SELECT EXTRACT(EPOCH FROM (now() - pg_postmaster_start_time())) as uptime"
            result = self.db_manager.execute_query(query)
            
            if result:
                uptime_seconds = float(result[0]['uptime'])
                uptime_hours = uptime_seconds / 3600
                
                if uptime_hours < 24:
                    return f"{uptime_hours:.1f} horas"
                else:
                    uptime_days = uptime_hours / 24
                    return f"{uptime_days:.1f} dias"
            
            return "Indisponível"
            
        except:
            return "Erro"
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Recupera resultado do cache se ainda válido"""
        if key in self.cache:
            cached_time, data = self.cache[key]
            if time.time() - cached_time < self.cache_ttl:
                return data
        return None
    
    def _cache_result(self, key: str, data: Any) -> None:
        """Armazena resultado no cache"""
        self.cache[key] = (time.time(), data)
    
    def _get_fallback_metrics(self) -> Dict[str, Any]:
        """Métricas de fallback em caso de erro"""
        return {
            'system_health': {'status': 'unknown', 'error': 'Não foi possível coletar métricas'},
            'database_stats': {'database_size': 'N/A', 'table_count': 0},
            'timestamp': datetime.now().isoformat()
        }