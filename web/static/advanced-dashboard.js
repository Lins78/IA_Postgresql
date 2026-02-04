// Biblioteca de Gráficos Avançados para Mamute Dashboard
class MamuteCharts {
    constructor() {
        this.charts = {};
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            }
        };
        
        // Carregar Chart.js se não estiver disponível
        this.loadChartJS();
    }

    async loadChartJS() {
        if (typeof Chart === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
            document.head.appendChild(script);
            
            await new Promise(resolve => {
                script.onload = resolve;
            });
        }
    }

    // Gráfico de Performance do Sistema
    createSystemHealthChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const config = {
            type: 'doughnut',
            data: {
                labels: ['CPU', 'Memória', 'Disco', 'Rede'],
                datasets: [{
                    data: [
                        data.cpu_usage || 45,
                        data.memory_usage || 67,
                        data.disk_usage || 23,
                        data.network_usage || 12
                    ],
                    backgroundColor: [
                        '#667eea',
                        '#764ba2', 
                        '#f093fb',
                        '#4facfe'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                ...this.defaultOptions,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        };

        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }
        this.charts[containerId] = new Chart(ctx, config);
        
        return this.charts[containerId];
    }

    // Gráfico de Atividade do Banco de Dados
    createDatabaseActivityChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const labels = data.timestamps || this.generateTimeLabels(24);
        
        const config = {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Consultas SELECT',
                        data: data.selects || this.generateRandomData(24, 50, 200),
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Operações INSERT/UPDATE',
                        data: data.writes || this.generateRandomData(24, 10, 50),
                        borderColor: '#764ba2',
                        backgroundColor: 'rgba(118, 75, 162, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Conexões Ativas',
                        data: data.connections || this.generateRandomData(24, 5, 25),
                        borderColor: '#f093fb',
                        backgroundColor: 'rgba(240, 147, 251, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                ...this.defaultOptions,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        };

        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }
        this.charts[containerId] = new Chart(ctx, config);
        
        return this.charts[containerId];
    }

    // Gráfico de Distribuição de Tamanho das Tabelas
    createTableSizesChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const tableData = data.largest_tables || [];
        const labels = tableData.map(t => t.tablename || `Tabela ${Math.random()}`);
        const sizes = tableData.map(t => t.size_bytes || Math.random() * 1000000);

        const config = {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Tamanho (bytes)',
                    data: sizes,
                    backgroundColor: [
                        '#667eea', '#764ba2', '#f093fb', '#4facfe', 
                        '#43e97b', '#38f9d7', '#ffeaa7', '#fab1a0'
                    ],
                    borderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                ...this.defaultOptions,
                indexAxis: 'y', // Horizontal bar
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return this.formatBytes(value);
                            }.bind(this)
                        }
                    }
                }
            }
        };

        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }
        this.charts[containerId] = new Chart(ctx, config);
        
        return this.charts[containerId];
    }

    // Gráfico de Cache Hit Ratio
    createCacheHitChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const hitRatio = data.cache_hit_ratio || 85.5;
        const missRatio = 100 - hitRatio;

        const config = {
            type: 'doughnut',
            data: {
                labels: ['Cache Hit', 'Cache Miss'],
                datasets: [{
                    data: [hitRatio, missRatio],
                    backgroundColor: [
                        hitRatio > 90 ? '#28a745' : hitRatio > 70 ? '#ffc107' : '#dc3545',
                        '#e9ecef'
                    ],
                    borderWidth: 3,
                    borderColor: '#fff'
                }]
            },
            options: {
                ...this.defaultOptions,
                cutout: '70%',
                plugins: {
                    legend: {
                        display: false
                    }
                }
            },
            plugins: [{
                id: 'centerText',
                beforeDraw: function(chart) {
                    const ctx = chart.ctx;
                    ctx.restore();
                    const fontSize = (chart.height / 114).toFixed(2);
                    ctx.font = `bold ${fontSize}em Segoe UI`;
                    ctx.textBaseline = "middle";
                    ctx.fillStyle = '#333';
                    
                    const text = `${hitRatio.toFixed(1)}%`;
                    const textX = Math.round((chart.width - ctx.measureText(text).width) / 2);
                    const textY = chart.height / 2;
                    
                    ctx.fillText(text, textX, textY);
                    ctx.save();
                }
            }]
        };

        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }
        this.charts[containerId] = new Chart(ctx, config);
        
        return this.charts[containerId];
    }

    // Gráfico de Tipos de Conexões
    createConnectionTypesChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const connectionData = data.by_state || [
            {state: 'active', count: 12},
            {state: 'idle', count: 8},
            {state: 'idle in transaction', count: 2}
        ];

        const labels = connectionData.map(c => c.state);
        const counts = connectionData.map(c => c.count);

        const config = {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: counts,
                    backgroundColor: [
                        '#28a745',  // active - green
                        '#6c757d',  // idle - gray
                        '#ffc107',  // idle in transaction - yellow
                        '#dc3545',  // error states - red
                        '#17a2b8'   // other - blue
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                ...this.defaultOptions,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        };

        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }
        this.charts[containerId] = new Chart(ctx, config);
        
        return this.charts[containerId];
    }

    // Gráfico de Performance ao Longo do Tempo
    createPerformanceTimelineChart(containerId, data) {
        const ctx = document.getElementById(containerId);
        if (!ctx) return null;

        const labels = this.generateTimeLabels(12);
        
        const config = {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Tempo Resposta (ms)',
                        data: data.response_times || this.generateRandomData(12, 50, 300),
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        yAxisID: 'y',
                        tension: 0.4
                    },
                    {
                        label: 'Throughput (req/s)',
                        data: data.throughput || this.generateRandomData(12, 10, 100),
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        yAxisID: 'y1',
                        tension: 0.4
                    }
                ]
            },
            options: {
                ...this.defaultOptions,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Tempo'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Tempo Resposta (ms)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Throughput (req/s)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        };

        if (this.charts[containerId]) {
            this.charts[containerId].destroy();
        }
        this.charts[containerId] = new Chart(ctx, config);
        
        return this.charts[containerId];
    }

    // Métodos utilitários
    generateTimeLabels(hours) {
        const labels = [];
        const now = new Date();
        
        for (let i = hours - 1; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 60 * 60 * 1000);
            labels.push(time.toLocaleTimeString('pt-BR', {hour: '2-digit', minute: '2-digit'}));
        }
        
        return labels;
    }

    generateRandomData(length, min, max) {
        return Array.from({length}, () => Math.floor(Math.random() * (max - min + 1)) + min);
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Atualizar dados dos gráficos
    updateChart(chartId, newData) {
        if (this.charts[chartId]) {
            const chart = this.charts[chartId];
            
            // Atualizar dados baseado no tipo
            if (chart.config.type === 'line') {
                // Adicionar novo ponto e remover o mais antigo
                chart.data.datasets.forEach((dataset, index) => {
                    if (newData.datasets && newData.datasets[index]) {
                        dataset.data = newData.datasets[index].data;
                    }
                });
                
                if (newData.labels) {
                    chart.data.labels = newData.labels;
                }
            } else {
                // Atualizar todos os dados
                if (newData.datasets) {
                    chart.data.datasets = newData.datasets;
                }
                if (newData.labels) {
                    chart.data.labels = newData.labels;
                }
            }
            
            chart.update('none'); // Sem animação para updates frequentes
        }
    }

    // Destruir todos os gráficos
    destroyAll() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};
    }

    // Redimensionar gráficos
    resizeAll() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.resize();
        });
    }
}

// Classe para gerenciar o dashboard avançado
class AdvancedDashboard {
    constructor() {
        this.charts = new MamuteCharts();
        this.refreshInterval = 30000; // 30 segundos
        this.intervalId = null;
        this.currentTheme = 'light';
        
        this.init();
    }

    async init() {
        await this.loadMetrics();
        this.setupEventListeners();
        this.startAutoRefresh();
    }

    async loadMetrics() {
        try {
            const response = await fetch('/metrics/advanced');
            if (!response.ok) {
                throw new Error(`Erro ${response.status}: ${response.statusText}`);
            }
            
            const metrics = await response.json();
            this.updateDashboard(metrics);
            
        } catch (error) {
            console.error('Erro ao carregar métricas:', error);
            this.showError('Erro ao carregar métricas do dashboard');
        }
    }

    updateDashboard(metrics) {
        // Atualizar cards de estatísticas
        this.updateStatsCards(metrics);
        
        // Atualizar gráficos
        this.updateCharts(metrics);
        
        // Atualizar alertas
        this.updateAlerts(metrics);
    }

    updateStatsCards(metrics) {
        const stats = metrics.database_stats || {};
        const performance = metrics.performance_metrics || {};
        
        // Atualizar cards principais
        this.updateCard('db-size', stats.database_size || 'N/A');
        this.updateCard('table-count', stats.table_count || 0);
        this.updateCard('cache-hit-ratio', `${performance.cache_hit_ratio || 0}%`);
        this.updateCard('active-connections', this.getActiveConnectionCount(metrics));
    }

    updateCharts(metrics) {
        // Sistema de saúde
        if (document.getElementById('systemHealthChart')) {
            this.charts.createSystemHealthChart('systemHealthChart', metrics.system_health || {});
        }

        // Atividade do banco
        if (document.getElementById('dbActivityChart')) {
            this.charts.createDatabaseActivityChart('dbActivityChart', metrics.recent_activity || {});
        }

        // Tamanhos das tabelas
        if (document.getElementById('tableSizesChart')) {
            this.charts.createTableSizesChart('tableSizesChart', metrics.storage_analysis || {});
        }

        // Cache hit ratio
        if (document.getElementById('cacheHitChart')) {
            this.charts.createCacheHitChart('cacheHitChart', metrics.performance_metrics || {});
        }

        // Tipos de conexões
        if (document.getElementById('connectionTypesChart')) {
            this.charts.createConnectionTypesChart('connectionTypesChart', metrics.connection_stats || {});
        }

        // Performance timeline
        if (document.getElementById('performanceChart')) {
            this.charts.createPerformanceTimelineChart('performanceChart', metrics.query_analytics || {});
        }
    }

    updateAlerts(metrics) {
        const alerts = [];
        
        // Verificar problemas de performance
        if (metrics.performance_metrics) {
            const cacheHit = metrics.performance_metrics.cache_hit_ratio || 0;
            if (cacheHit < 80) {
                alerts.push({
                    type: 'warning',
                    title: 'Cache Hit Ratio Baixo',
                    message: `Taxa de acerto do cache: ${cacheHit}% (recomendado: >80%)`,
                    action: 'Considere ajustar configurações de memória'
                });
            }

            const vacuumCandidates = metrics.performance_metrics.vacuum_candidates || [];
            if (vacuumCandidates.length > 0) {
                alerts.push({
                    type: 'info',
                    title: 'VACUUM Necessário',
                    message: `${vacuumCandidates.length} tabela(s) precisam de manutenção`,
                    action: 'Execute VACUUM ANALYZE nas tabelas indicadas'
                });
            }
        }

        this.displayAlerts(alerts);
    }

    displayAlerts(alerts) {
        const container = document.getElementById('alertsContainer');
        if (!container) return;

        container.innerHTML = '';

        alerts.forEach(alert => {
            const alertElement = document.createElement('div');
            alertElement.className = `alert alert-${alert.type}`;
            alertElement.innerHTML = `
                <div class="alert-header">
                    <strong>${alert.title}</strong>
                    <button type="button" class="alert-close">&times;</button>
                </div>
                <div class="alert-body">
                    <p>${alert.message}</p>
                    ${alert.action ? `<small><strong>Ação:</strong> ${alert.action}</small>` : ''}
                </div>
            `;

            // Adicionar evento de fechar
            alertElement.querySelector('.alert-close').addEventListener('click', () => {
                alertElement.remove();
            });

            container.appendChild(alertElement);
        });
    }

    setupEventListeners() {
        // Botão de refresh manual
        const refreshBtn = document.getElementById('refreshDashboard');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadMetrics());
        }

        // Toggle auto-refresh
        const autoRefreshToggle = document.getElementById('autoRefresh');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.startAutoRefresh();
                } else {
                    this.stopAutoRefresh();
                }
            });
        }

        // Redimensionar gráficos quando janela redimensiona
        window.addEventListener('resize', () => {
            this.charts.resizeAll();
        });
    }

    startAutoRefresh() {
        this.stopAutoRefresh(); // Parar qualquer interval existente
        
        this.intervalId = setInterval(() => {
            this.loadMetrics();
        }, this.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    // Métodos utilitários
    updateCard(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    getActiveConnectionCount(metrics) {
        if (metrics.connection_stats && metrics.connection_stats.by_state) {
            const active = metrics.connection_stats.by_state.find(s => s.state === 'active');
            return active ? active.count : 0;
        }
        return 0;
    }

    showError(message) {
        const errorContainer = document.getElementById('errorContainer');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="alert alert-error">
                    <strong>Erro:</strong> ${message}
                </div>
            `;

            setTimeout(() => {
                errorContainer.innerHTML = '';
            }, 5000);
        }
    }
}

// Inicializar dashboard quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.advanced-dashboard')) {
        window.advancedDashboard = new AdvancedDashboard();
    }
});

// Exportar classes
window.MamuteCharts = MamuteCharts;
window.AdvancedDashboard = AdvancedDashboard;