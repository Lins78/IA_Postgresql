"""
Sistema de Relatórios Automatizados do Mamute
Geração automática de relatórios em PDF, HTML e Excel
"""
import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from jinja2 import Template
import time
from threading import Thread

# Tentar importar bibliotecas opcionais
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    plt = None
    sns = None

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    schedule = None
import base64
import io

# Adicionar o diretório principal ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.config import Config
from src.utils.logger import setup_logger
from src.database.connection import DatabaseManager

class ReportGenerator:
    """Gerador de relatórios automatizados do Mamute"""
    
    def __init__(self, config_file: str = ".env"):
        """Inicializar gerador de relatórios"""
        self.config = Config(config_file)
        self.logger = setup_logger("ReportGenerator")
        self.db_manager = DatabaseManager(self.config)
        
        # Diretórios de relatórios
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        # Subdiretórios por tipo
        self.daily_dir = self.reports_dir / "daily"
        self.weekly_dir = self.reports_dir / "weekly"
        self.monthly_dir = self.reports_dir / "monthly"
        self.custom_dir = self.reports_dir / "custom"
        
        for dir_path in [self.daily_dir, self.weekly_dir, self.monthly_dir, self.custom_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Templates HTML
        self.templates_dir = Path("web/templates/reports")
        self.templates_dir.mkdir(exist_ok=True)
        
        # Configuração de estilo para gráficos
        if PLOTTING_AVAILABLE:
            try:
                plt.style.use('seaborn-v0_8-darkgrid')
                sns.set_palette("husl")
            except:
                # Fallback para estilo padrão se seaborn style não disponível
                pass
        else:
            self.logger.warning("Matplotlib/Seaborn não disponíveis - gráficos desabilitados")
        
        # Agendador de relatórios automáticos
        self.scheduler_active = False
        self.scheduler_thread = None
        
        self._create_html_templates()
        
        self.logger.info("Sistema de relatórios automatizados inicializado")
    
    def _create_html_templates(self):
        """Criar templates HTML para relatórios"""
        # Template principal
        main_template = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ title }} - Mamute IA PostgreSQL</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0; padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 30px; border-radius: 10px;
            text-align: center; margin-bottom: 30px;
        }
        .header h1 { margin: 0; font-size: 2.5em; }
        .header p { margin: 10px 0 0 0; opacity: 0.9; }
        .section {
            background: white; padding: 25px;
            margin: 20px 0; border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .metrics-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px; margin: 20px 0;
        }
        .metric-card {
            background: #f8f9fa; padding: 20px;
            border-radius: 8px; text-align: center;
            border-left: 4px solid #667eea;
        }
        .metric-value { font-size: 2.5em; font-weight: bold; color: #667eea; }
        .metric-label { color: #666; margin-top: 5px; }
        .chart-container { margin: 20px 0; text-align: center; }
        .table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .table th, .table td { 
            padding: 12px; text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .table th { background: #f8f9fa; font-weight: 600; }
        .alert { padding: 15px; margin: 10px 0; border-radius: 5px; }
        .alert-warning { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }
        .alert-error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .alert-success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .footer {
            text-align: center; margin-top: 40px;
            color: #666; font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🐘 {{ title }}</h1>
        <p>Relatório gerado em {{ timestamp }}</p>
    </div>
    
    {{ content }}
    
    <div class="footer">
        <p>Relatório gerado automaticamente pelo Mamute - IA PostgreSQL<br>
        Sistema desenvolvido para análise inteligente de dados</p>
    </div>
</body>
</html>
        '''
        
        template_file = self.templates_dir / "main_template.html"
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(main_template)
    
    def generate_daily_report(self, target_date: Optional[datetime] = None) -> str:
        """Gerar relatório diário"""
        try:
            if not target_date:
                target_date = datetime.now()
            
            date_str = target_date.strftime("%Y-%m-%d")
            
            self.logger.info(f"Gerando relatório diário para {date_str}")
            
            # Coletar dados do dia
            start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            # Estatísticas de conversas
            conversation_stats = self.db_manager.execute_query("""
                SELECT 
                    COUNT(*) as total_conversations,
                    COUNT(DISTINCT session_id) as unique_sessions,
                    AVG(LENGTH(user_message)) as avg_message_length,
                    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '1 hour') as last_hour_conversations
                FROM conversations 
                WHERE created_at >= %(start_date)s AND created_at < %(end_date)s
            """, {'start_date': start_date, 'end_date': end_date})
            
            # Documentos adicionados
            document_stats = self.db_manager.execute_query("""
                SELECT 
                    COUNT(*) as total_documents,
                    COUNT(DISTINCT category) as unique_categories,
                    AVG(LENGTH(content)) as avg_content_length
                FROM documents 
                WHERE created_at >= %(start_date)s AND created_at < %(end_date)s
            """, {'start_date': start_date, 'end_date': end_date})
            
            # Atividade por hora
            hourly_activity = self.db_manager.execute_query("""
                SELECT 
                    EXTRACT(HOUR FROM created_at) as hour,
                    COUNT(*) as conversations
                FROM conversations 
                WHERE created_at >= %(start_date)s AND created_at < %(end_date)s
                GROUP BY EXTRACT(HOUR FROM created_at)
                ORDER BY hour
            """, {'start_date': start_date, 'end_date': end_date})
            
            # Top categorias de documentos
            top_categories = self.db_manager.execute_query("""
                SELECT 
                    category,
                    COUNT(*) as document_count
                FROM documents 
                WHERE created_at >= %(start_date)s AND created_at < %(end_date)s
                  AND category IS NOT NULL
                GROUP BY category
                ORDER BY document_count DESC
                LIMIT 10
            """, {'start_date': start_date, 'end_date': end_date})
            
            # Gerar gráficos
            charts = self._generate_daily_charts(hourly_activity, top_categories)
            
            # Compilar dados do relatório
            report_data = {
                'date': date_str,
                'conversation_stats': conversation_stats[0] if conversation_stats else {},
                'document_stats': document_stats[0] if document_stats else {},
                'hourly_activity': hourly_activity or [],
                'top_categories': top_categories or [],
                'charts': charts
            }
            
            # Gerar HTML
            html_content = self._generate_daily_html(report_data)
            
            # Salvar relatório
            filename = f"daily_report_{date_str}.html"
            report_path = self.daily_dir / filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Gerar também em JSON para APIs
            json_path = self.daily_dir / f"daily_report_{date_str}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str, ensure_ascii=False)
            
            self.logger.info(f"Relatório diário salvo: {report_path}")
            
            return str(report_path)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório diário: {e}")
            return ""
    
    def generate_weekly_report(self, target_date: Optional[datetime] = None) -> str:
        """Gerar relatório semanal"""
        try:
            if not target_date:
                target_date = datetime.now()
            
            # Início da semana (segunda-feira)
            days_since_monday = target_date.weekday()
            week_start = target_date - timedelta(days=days_since_monday)
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            week_end = week_start + timedelta(days=7)
            
            week_str = f"{week_start.strftime('%Y-%m-%d')}_to_{(week_end - timedelta(days=1)).strftime('%Y-%m-%d')}"
            
            self.logger.info(f"Gerando relatório semanal para {week_str}")
            
            # Estatísticas da semana
            weekly_stats = self.db_manager.execute_query("""
                SELECT 
                    COUNT(*) FILTER (WHERE created_at >= %(week_start)s AND created_at < %(week_end)s) as total_conversations,
                    COUNT(DISTINCT session_id) FILTER (WHERE created_at >= %(week_start)s AND created_at < %(week_end)s) as unique_sessions,
                    AVG(LENGTH(user_message)) FILTER (WHERE created_at >= %(week_start)s AND created_at < %(week_end)s) as avg_message_length,
                    COUNT(*) FILTER (WHERE created_at >= %(week_start)s - INTERVAL '7 days' AND created_at < %(week_start)s) as prev_week_conversations
                FROM conversations
            """, {'week_start': week_start, 'week_end': week_end})
            
            # Atividade diária da semana
            daily_activity = self.db_manager.execute_query("""
                SELECT 
                    DATE(created_at) as day,
                    COUNT(*) as conversations,
                    COUNT(DISTINCT session_id) as sessions
                FROM conversations 
                WHERE created_at >= %(week_start)s AND created_at < %(week_end)s
                GROUP BY DATE(created_at)
                ORDER BY day
            """, {'week_start': week_start, 'week_end': week_end})
            
            # Documentos por categoria na semana
            weekly_documents = self.db_manager.execute_query("""
                SELECT 
                    category,
                    COUNT(*) as document_count,
                    AVG(LENGTH(content)) as avg_length
                FROM documents 
                WHERE created_at >= %(week_start)s AND created_at < %(week_end)s
                  AND category IS NOT NULL
                GROUP BY category
                ORDER BY document_count DESC
            """, {'week_start': week_start, 'week_end': week_end})
            
            # Tendências e comparações
            growth_rate = 0
            if weekly_stats and weekly_stats[0]['prev_week_conversations']:
                current = weekly_stats[0]['total_conversations']
                previous = weekly_stats[0]['prev_week_conversations']
                growth_rate = ((current - previous) / previous) * 100 if previous > 0 else 0
            
            # Gerar gráficos
            charts = self._generate_weekly_charts(daily_activity, weekly_documents)
            
            # Compilar dados do relatório
            report_data = {
                'week_period': week_str,
                'week_start': week_start.strftime('%Y-%m-%d'),
                'week_end': (week_end - timedelta(days=1)).strftime('%Y-%m-%d'),
                'weekly_stats': weekly_stats[0] if weekly_stats else {},
                'growth_rate': growth_rate,
                'daily_activity': daily_activity or [],
                'weekly_documents': weekly_documents or [],
                'charts': charts
            }
            
            # Gerar HTML
            html_content = self._generate_weekly_html(report_data)
            
            # Salvar relatório
            filename = f"weekly_report_{week_str}.html"
            report_path = self.weekly_dir / filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Gerar também em JSON
            json_path = self.weekly_dir / f"weekly_report_{week_str}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str, ensure_ascii=False)
            
            self.logger.info(f"Relatório semanal salvo: {report_path}")
            
            return str(report_path)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório semanal: {e}")
            return ""
    
    def generate_monthly_report(self, target_date: Optional[datetime] = None) -> str:
        """Gerar relatório mensal"""
        try:
            if not target_date:
                target_date = datetime.now()
            
            # Primeiro e último dia do mês
            month_start = target_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if month_start.month == 12:
                month_end = month_start.replace(year=month_start.year + 1, month=1)
            else:
                month_end = month_start.replace(month=month_start.month + 1)
            
            month_str = target_date.strftime("%Y-%m")
            
            self.logger.info(f"Gerando relatório mensal para {month_str}")
            
            # Estatísticas mensais detalhadas
            monthly_stats = self.db_manager.execute_query("""
                SELECT 
                    COUNT(*) as total_conversations,
                    COUNT(DISTINCT session_id) as unique_sessions,
                    COUNT(DISTINCT DATE(created_at)) as active_days,
                    AVG(LENGTH(user_message)) as avg_message_length,
                    MIN(created_at) as first_conversation,
                    MAX(created_at) as last_conversation
                FROM conversations 
                WHERE created_at >= %(month_start)s AND created_at < %(month_end)s
            """, {'month_start': month_start, 'month_end': month_end})
            
            # Atividade semanal do mês
            weekly_activity = self.db_manager.execute_query("""
                SELECT 
                    EXTRACT(WEEK FROM created_at) as week_number,
                    COUNT(*) as conversations,
                    COUNT(DISTINCT session_id) as sessions
                FROM conversations 
                WHERE created_at >= %(month_start)s AND created_at < %(month_end)s
                GROUP BY EXTRACT(WEEK FROM created_at)
                ORDER BY week_number
            """, {'month_start': month_start, 'month_end': month_end})
            
            # Top usuários (por sessões)
            top_users = self.db_manager.execute_query("""
                SELECT 
                    session_id,
                    COUNT(*) as conversation_count,
                    MIN(created_at) as first_interaction,
                    MAX(created_at) as last_interaction
                FROM conversations 
                WHERE created_at >= %(month_start)s AND created_at < %(month_end)s
                GROUP BY session_id
                ORDER BY conversation_count DESC
                LIMIT 10
            """, {'month_start': month_start, 'month_end': month_end})
            
            # Documentos do mês
            monthly_documents = self.db_manager.execute_query("""
                SELECT 
                    COUNT(*) as total_documents,
                    COUNT(DISTINCT category) as unique_categories,
                    AVG(LENGTH(content)) as avg_content_length,
                    COUNT(DISTINCT source) as unique_sources
                FROM documents 
                WHERE created_at >= %(month_start)s AND created_at < %(month_end)s
            """, {'month_start': month_start, 'month_end': month_end})
            
            # Performance metrics do mês (se disponível)
            performance_summary = self._get_monthly_performance_summary(month_start, month_end)
            
            # Gerar gráficos
            charts = self._generate_monthly_charts(weekly_activity, top_users, monthly_documents)
            
            # Compilar dados do relatório
            report_data = {
                'month_period': month_str,
                'month_name': target_date.strftime('%B %Y'),
                'month_start': month_start.strftime('%Y-%m-%d'),
                'month_end': (month_end - timedelta(days=1)).strftime('%Y-%m-%d'),
                'monthly_stats': monthly_stats[0] if monthly_stats else {},
                'weekly_activity': weekly_activity or [],
                'top_users': top_users or [],
                'monthly_documents': monthly_documents[0] if monthly_documents else {},
                'performance_summary': performance_summary,
                'charts': charts
            }
            
            # Gerar HTML
            html_content = self._generate_monthly_html(report_data)
            
            # Salvar relatório
            filename = f"monthly_report_{month_str}.html"
            report_path = self.monthly_dir / filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Gerar também em JSON e Excel
            json_path = self.monthly_dir / f"monthly_report_{month_str}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str, ensure_ascii=False)
            
            # Gerar Excel com múltiplas abas
            excel_path = self.monthly_dir / f"monthly_report_{month_str}.xlsx"
            self._generate_excel_report(report_data, excel_path)
            
            self.logger.info(f"Relatório mensal salvo: {report_path}")
            
            return str(report_path)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório mensal: {e}")
            return ""
    
    def _generate_daily_charts(self, hourly_activity: List[Dict], top_categories: List[Dict]) -> Dict[str, str]:
        """Gerar gráficos para relatório diário"""
        charts = {}
        
        if not PLOTTING_AVAILABLE:
            self.logger.warning("Matplotlib não disponível - gráficos desabilitados")
            return charts
        
        try:
            # Gráfico de atividade por hora
            if hourly_activity:
                fig, ax = plt.subplots(figsize=(12, 6))
                hours = [item['hour'] for item in hourly_activity]
                conversations = [item['conversations'] for item in hourly_activity]
                
                ax.bar(hours, conversations, color='skyblue', alpha=0.7)
                ax.set_xlabel('Hora do Dia')
                ax.set_ylabel('Número de Conversas')
                ax.set_title('Atividade por Hora')
                ax.set_xticks(range(24))
                
                # Salvar como base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
                buffer.seek(0)
                chart_base64 = base64.b64encode(buffer.getvalue()).decode()
                charts['hourly_activity'] = f"data:image/png;base64,{chart_base64}"
                
                plt.close()
            
            # Gráfico de categorias
            if top_categories:
                fig, ax = plt.subplots(figsize=(10, 8))
                categories = [item['category'] for item in top_categories[:8]]
                counts = [item['document_count'] for item in top_categories[:8]]
                
                ax.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)
                ax.set_title('Distribuição de Documentos por Categoria')
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
                buffer.seek(0)
                chart_base64 = base64.b64encode(buffer.getvalue()).decode()
                charts['categories_pie'] = f"data:image/png;base64,{chart_base64}"
                
                plt.close()
            
        except Exception as e:
            self.logger.warning(f"Erro ao gerar gráficos diários: {e}")
        
        return charts
    
    def _generate_weekly_charts(self, daily_activity: List[Dict], weekly_documents: List[Dict]) -> Dict[str, str]:
        """Gerar gráficos para relatório semanal"""
        charts = {}
        
        try:
            # Gráfico de atividade diária
            if daily_activity:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
                
                days = [item['day'].strftime('%a %d/%m') for item in daily_activity]
                conversations = [item['conversations'] for item in daily_activity]
                sessions = [item['sessions'] for item in daily_activity]
                
                ax1.plot(days, conversations, marker='o', linewidth=2, markersize=6, color='blue', label='Conversas')
                ax1.set_title('Conversas por Dia da Semana')
                ax1.set_ylabel('Número de Conversas')
                ax1.tick_params(axis='x', rotation=45)
                ax1.grid(True, alpha=0.3)
                
                ax2.plot(days, sessions, marker='s', linewidth=2, markersize=6, color='green', label='Sessões')
                ax2.set_title('Sessões Únicas por Dia')
                ax2.set_ylabel('Número de Sessões')
                ax2.set_xlabel('Dia da Semana')
                ax2.tick_params(axis='x', rotation=45)
                ax2.grid(True, alpha=0.3)
                
                plt.tight_layout()
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
                buffer.seek(0)
                chart_base64 = base64.b64encode(buffer.getvalue()).decode()
                charts['weekly_activity'] = f"data:image/png;base64,{chart_base64}"
                
                plt.close()
            
        except Exception as e:
            self.logger.warning(f"Erro ao gerar gráficos semanais: {e}")
        
        return charts
    
    def _generate_monthly_charts(self, weekly_activity: List[Dict], top_users: List[Dict], monthly_documents: Dict) -> Dict[str, str]:
        """Gerar gráficos para relatório mensal"""
        charts = {}
        
        try:
            # Gráfico de atividade semanal
            if weekly_activity:
                fig, ax = plt.subplots(figsize=(12, 6))
                
                weeks = [f"Semana {int(item['week_number'])}" for item in weekly_activity]
                conversations = [item['conversations'] for item in weekly_activity]
                
                bars = ax.bar(weeks, conversations, color='coral', alpha=0.7)
                ax.set_title('Atividade Semanal do Mês')
                ax.set_ylabel('Número de Conversas')
                ax.set_xlabel('Semana')
                
                # Adicionar valores nas barras
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}', ha='center', va='bottom')
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
                buffer.seek(0)
                chart_base64 = base64.b64encode(buffer.getvalue()).decode()
                charts['monthly_activity'] = f"data:image/png;base64,{chart_base64}"
                
                plt.close()
            
        except Exception as e:
            self.logger.warning(f"Erro ao gerar gráficos mensais: {e}")
        
        return charts
    
    def _generate_daily_html(self, data: Dict) -> str:
        """Gerar HTML para relatório diário"""
        content = f"""
        <div class="section">
            <h2>📊 Resumo do Dia - {data['date']}</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{data['conversation_stats'].get('total_conversations', 0)}</div>
                    <div class="metric-label">Conversas Total</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{data['conversation_stats'].get('unique_sessions', 0)}</div>
                    <div class="metric-label">Sessões Únicas</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{data['document_stats'].get('total_documents', 0)}</div>
                    <div class="metric-label">Documentos Adicionados</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{data['conversation_stats'].get('last_hour_conversations', 0)}</div>
                    <div class="metric-label">Última Hora</div>
                </div>
            </div>
        </div>
        """
        
        if data.get('charts', {}).get('hourly_activity'):
            content += f"""
            <div class="section">
                <h3>📈 Atividade por Hora</h3>
                <div class="chart-container">
                    <img src="{data['charts']['hourly_activity']}" alt="Atividade Horária" style="max-width: 100%; height: auto;">
                </div>
            </div>
            """
        
        if data.get('charts', {}).get('categories_pie'):
            content += f"""
            <div class="section">
                <h3>📂 Distribuição por Categoria</h3>
                <div class="chart-container">
                    <img src="{data['charts']['categories_pie']}" alt="Categorias" style="max-width: 100%; height: auto;">
                </div>
            </div>
            """
        
        # Carregar template e renderizar
        template_file = self.templates_dir / "main_template.html"
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        template = Template(template_content)
        return template.render(
            title=f"Relatório Diário - {data['date']}",
            timestamp=datetime.now().strftime('%d/%m/%Y às %H:%M'),
            content=content
        )
    
    def _generate_weekly_html(self, data: Dict) -> str:
        """Gerar HTML para relatório semanal"""
        growth_indicator = "📈" if data['growth_rate'] > 0 else "📉" if data['growth_rate'] < 0 else "➡️"
        
        content = f"""
        <div class="section">
            <h2>📅 Resumo Semanal - {data['week_start']} a {data['week_end']}</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{data['weekly_stats'].get('total_conversations', 0)}</div>
                    <div class="metric-label">Conversas na Semana</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{data['weekly_stats'].get('unique_sessions', 0)}</div>
                    <div class="metric-label">Sessões Únicas</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{growth_indicator} {data['growth_rate']:.1f}%</div>
                    <div class="metric-label">Crescimento vs. Semana Anterior</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{len(data['daily_activity'])}</div>
                    <div class="metric-label">Dias Ativos</div>
                </div>
            </div>
        </div>
        """
        
        if data.get('charts', {}).get('weekly_activity'):
            content += f"""
            <div class="section">
                <h3>📊 Atividade Diária da Semana</h3>
                <div class="chart-container">
                    <img src="{data['charts']['weekly_activity']}" alt="Atividade Semanal" style="max-width: 100%; height: auto;">
                </div>
            </div>
            """
        
        # Tabela de documentos por categoria
        if data['weekly_documents']:
            content += """
            <div class="section">
                <h3>📚 Documentos por Categoria</h3>
                <table class="table">
                    <tr><th>Categoria</th><th>Quantidade</th><th>Tamanho Médio</th></tr>
            """
            for doc in data['weekly_documents'][:10]:
                content += f"""
                    <tr>
                        <td>{doc['category']}</td>
                        <td>{doc['document_count']}</td>
                        <td>{doc['avg_length']:.0f} caracteres</td>
                    </tr>
                """
            content += "</table></div>"
        
        # Carregar template e renderizar
        template_file = self.templates_dir / "main_template.html"
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        template = Template(template_content)
        return template.render(
            title=f"Relatório Semanal - {data['week_period']}",
            timestamp=datetime.now().strftime('%d/%m/%Y às %H:%M'),
            content=content
        )
    
    def _generate_monthly_html(self, data: Dict) -> str:
        """Gerar HTML para relatório mensal"""
        content = f"""
        <div class="section">
            <h2>📆 Resumo Mensal - {data['month_name']}</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{data['monthly_stats'].get('total_conversations', 0)}</div>
                    <div class="metric-label">Total de Conversas</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{data['monthly_stats'].get('unique_sessions', 0)}</div>
                    <div class="metric-label">Sessões Únicas</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{data['monthly_stats'].get('active_days', 0)}</div>
                    <div class="metric-label">Dias Ativos</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{data['monthly_documents'].get('total_documents', 0)}</div>
                    <div class="metric-label">Documentos</div>
                </div>
            </div>
        </div>
        """
        
        if data.get('charts', {}).get('monthly_activity'):
            content += f"""
            <div class="section">
                <h3>📈 Atividade Semanal do Mês</h3>
                <div class="chart-container">
                    <img src="{data['charts']['monthly_activity']}" alt="Atividade Mensal" style="max-width: 100%; height: auto;">
                </div>
            </div>
            """
        
        # Top usuários
        if data['top_users']:
            content += """
            <div class="section">
                <h3>👥 Usuários Mais Ativos</h3>
                <table class="table">
                    <tr><th>Sessão</th><th>Conversas</th><th>Primeira Interação</th><th>Última Interação</th></tr>
            """
            for user in data['top_users'][:10]:
                content += f"""
                    <tr>
                        <td>{user['session_id'][:8]}...</td>
                        <td>{user['conversation_count']}</td>
                        <td>{user['first_interaction'].strftime('%d/%m %H:%M') if user['first_interaction'] else 'N/A'}</td>
                        <td>{user['last_interaction'].strftime('%d/%m %H:%M') if user['last_interaction'] else 'N/A'}</td>
                    </tr>
                """
            content += "</table></div>"
        
        # Carregar template e renderizar
        template_file = self.templates_dir / "main_template.html"
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        template = Template(template_content)
        return template.render(
            title=f"Relatório Mensal - {data['month_name']}",
            timestamp=datetime.now().strftime('%d/%m/%Y às %H:%M'),
            content=content
        )
    
    def _generate_excel_report(self, data: Dict, file_path: Path):
        """Gerar relatório em Excel com múltiplas abas"""
        try:
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                # Aba de resumo
                summary_data = pd.DataFrame([data['monthly_stats']])
                summary_data.to_excel(writer, sheet_name='Resumo', index=False)
                
                # Aba de atividade semanal
                if data['weekly_activity']:
                    weekly_df = pd.DataFrame(data['weekly_activity'])
                    weekly_df.to_excel(writer, sheet_name='Atividade Semanal', index=False)
                
                # Aba de top usuários
                if data['top_users']:
                    users_df = pd.DataFrame(data['top_users'])
                    users_df.to_excel(writer, sheet_name='Top Usuários', index=False)
                
                # Aba de documentos
                doc_data = pd.DataFrame([data['monthly_documents']])
                doc_data.to_excel(writer, sheet_name='Documentos', index=False)
            
        except Exception as e:
            self.logger.warning(f"Erro ao gerar Excel: {e}")
    
    def _get_monthly_performance_summary(self, month_start: datetime, month_end: datetime) -> Dict[str, Any]:
        """Obter resumo de performance do mês"""
        try:
            # Placeholder para métricas de performance
            # Integração futura com performance_analyzer
            return {
                'avg_response_time': 0.5,
                'system_uptime': 99.9,
                'error_rate': 0.1
            }
        except:
            return {}
    
    def schedule_automatic_reports(self):
        """Agendar geração automática de relatórios"""
        if not SCHEDULE_AVAILABLE:
            self.logger.warning("Biblioteca 'schedule' não disponível - agendamento automático desabilitado")
            self.logger.info("Instale com: pip install schedule")
            return
        
        def generate_daily():
            try:
                self.generate_daily_report()
                self.logger.info("Relatório diário automático gerado")
            except Exception as e:
                self.logger.error(f"Erro no relatório diário automático: {e}")
        
        def generate_weekly():
            try:
                self.generate_weekly_report()
                self.logger.info("Relatório semanal automático gerado")
            except Exception as e:
                self.logger.error(f"Erro no relatório semanal automático: {e}")
        
        def generate_monthly():
            try:
                self.generate_monthly_report()
                self.logger.info("Relatório mensal automático gerado")
            except Exception as e:
                self.logger.error(f"Erro no relatório mensal automático: {e}")
        
        def scheduler_loop():
            while self.scheduler_active:
                schedule.run_pending()
                time.sleep(60)
        
        # Agendar relatórios
        schedule.every().day.at("08:00").do(generate_daily)
        schedule.every().monday.at("09:00").do(generate_weekly)
        schedule.every().month.at("10:00").do(generate_monthly)
        
        self.scheduler_active = True
        self.scheduler_thread = Thread(target=scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Agendamento automático de relatórios iniciado")
        self.logger.info("- Relatórios diários: 08:00")
        self.logger.info("- Relatórios semanais: Segunda-feira 09:00")
        self.logger.info("- Relatórios mensais: Primeiro dia do mês 10:00")
    
    def list_reports(self, report_type: str = "all") -> List[Dict[str, Any]]:
        """Listar relatórios disponíveis"""
        reports = []
        
        try:
            search_dirs = []
            if report_type in ["all", "daily"]:
                search_dirs.append((self.daily_dir, "daily"))
            if report_type in ["all", "weekly"]:
                search_dirs.append((self.weekly_dir, "weekly"))
            if report_type in ["all", "monthly"]:
                search_dirs.append((self.monthly_dir, "monthly"))
            if report_type in ["all", "custom"]:
                search_dirs.append((self.custom_dir, "custom"))
            
            for directory, rtype in search_dirs:
                for file_path in directory.glob("*.html"):
                    stat = file_path.stat()
                    reports.append({
                        'name': file_path.stem,
                        'type': rtype,
                        'file_path': str(file_path),
                        'size_mb': round(stat.st_size / (1024*1024), 2),
                        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            # Ordenar por data de criação (mais recente primeiro)
            reports.sort(key=lambda x: x['created_at'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Erro ao listar relatórios: {e}")
        
        return reports

# Instância global do gerador de relatórios
report_generator = ReportGenerator()

def main():
    """Função principal para demonstrar sistema de relatórios"""
    print("🐘 SISTEMA DE RELATÓRIOS AUTOMATIZADOS DO MAMUTE")
    print("=" * 60)
    
    try:
        # Gerar relatórios de exemplo
        print("\\n📊 Gerando relatório diário...")
        daily_report = report_generator.generate_daily_report()
        if daily_report:
            print(f"✅ Relatório diário salvo: {Path(daily_report).name}")
        
        print("\\n📅 Gerando relatório semanal...")
        weekly_report = report_generator.generate_weekly_report()
        if weekly_report:
            print(f"✅ Relatório semanal salvo: {Path(weekly_report).name}")
        
        print("\\n📆 Gerando relatório mensal...")
        monthly_report = report_generator.generate_monthly_report()
        if monthly_report:
            print(f"✅ Relatório mensal salvo: {Path(monthly_report).name}")
        
        # Listar relatórios disponíveis
        print("\\n📋 Relatórios disponíveis:")
        reports = report_generator.list_reports()
        for report in reports[:5]:  # Mostrar apenas os 5 mais recentes
            print(f"   - {report['name']} ({report['type']}) - {report['size_mb']} MB")
        
        print("\\n✅ Sistema de relatórios automatizados configurado!")
        print("💡 Use report_generator.schedule_automatic_reports() para agendamento automático")
        print(f"📁 Relatórios salvos em: {report_generator.reports_dir}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()