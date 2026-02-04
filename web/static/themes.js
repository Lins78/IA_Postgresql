// Sistema de Temas para o Mamute
class ThemeManager {
    constructor() {
        this.themes = {
            light: {
                name: 'Modo Claro',
                icon: '☀️',
                properties: {
                    '--primary-color': '#4a90e2',
                    '--primary-dark': '#357abd',
                    '--secondary-color': '#f8f9fa',
                    '--accent-color': '#28a745',
                    '--warning-color': '#ffc107',
                    '--danger-color': '#dc3545',
                    '--background-color': '#ffffff',
                    '--surface-color': '#f8f9fa',
                    '--card-background': '#ffffff',
                    '--text-color': '#212529',
                    '--text-muted': '#6c757d',
                    '--border-color': '#dee2e6',
                    '--input-background': '#ffffff',
                    '--button-background': '#4a90e2',
                    '--button-text': '#ffffff',
                    '--shadow-color': 'rgba(0, 0, 0, 0.1)',
                    '--chat-user-bg': '#e3f2fd',
                    '--chat-assistant-bg': '#f5f5f5',
                    '--sidebar-background': '#f8f9fa',
                    '--header-background': '#4a90e2',
                    '--code-background': '#f8f9fa',
                    '--code-border': '#dee2e6'
                }
            },
            dark: {
                name: 'Modo Escuro',
                icon: '🌙',
                properties: {
                    '--primary-color': '#64b5f6',
                    '--primary-dark': '#42a5f5',
                    '--secondary-color': '#1e1e1e',
                    '--accent-color': '#66bb6a',
                    '--warning-color': '#ffb74d',
                    '--danger-color': '#e57373',
                    '--background-color': '#121212',
                    '--surface-color': '#1e1e1e',
                    '--card-background': '#2d2d2d',
                    '--text-color': '#ffffff',
                    '--text-muted': '#aaaaaa',
                    '--border-color': '#404040',
                    '--input-background': '#2d2d2d',
                    '--button-background': '#64b5f6',
                    '--button-text': '#000000',
                    '--shadow-color': 'rgba(0, 0, 0, 0.3)',
                    '--chat-user-bg': '#263238',
                    '--chat-assistant-bg': '#2d2d2d',
                    '--sidebar-background': '#1e1e1e',
                    '--header-background': '#2d2d2d',
                    '--code-background': '#1e1e1e',
                    '--code-border': '#404040'
                }
            },
            blue: {
                name: 'Oceano Azul',
                icon: '🌊',
                properties: {
                    '--primary-color': '#0277bd',
                    '--primary-dark': '#01579b',
                    '--secondary-color': '#e1f5fe',
                    '--accent-color': '#00acc1',
                    '--warning-color': '#ff8f00',
                    '--danger-color': '#d32f2f',
                    '--background-color': '#f0f8ff',
                    '--surface-color': '#e1f5fe',
                    '--card-background': '#ffffff',
                    '--text-color': '#0d47a1',
                    '--text-muted': '#546e7a',
                    '--border-color': '#b3e5fc',
                    '--input-background': '#ffffff',
                    '--button-background': '#0277bd',
                    '--button-text': '#ffffff',
                    '--shadow-color': 'rgba(2, 119, 189, 0.1)',
                    '--chat-user-bg': '#e3f2fd',
                    '--chat-assistant-bg': '#f1f8e9',
                    '--sidebar-background': '#e1f5fe',
                    '--header-background': '#0277bd',
                    '--code-background': '#e1f5fe',
                    '--code-border': '#b3e5fc'
                }
            },
            green: {
                name: 'Natureza Verde',
                icon: '🌿',
                properties: {
                    '--primary-color': '#2e7d32',
                    '--primary-dark': '#1b5e20',
                    '--secondary-color': '#e8f5e8',
                    '--accent-color': '#4caf50',
                    '--warning-color': '#ff8f00',
                    '--danger-color': '#d32f2f',
                    '--background-color': '#f1f8e9',
                    '--surface-color': '#e8f5e8',
                    '--card-background': '#ffffff',
                    '--text-color': '#1b5e20',
                    '--text-muted': '#4e342e',
                    '--border-color': '#c8e6c9',
                    '--input-background': '#ffffff',
                    '--button-background': '#2e7d32',
                    '--button-text': '#ffffff',
                    '--shadow-color': 'rgba(46, 125, 50, 0.1)',
                    '--chat-user-bg': '#e8f5e8',
                    '--chat-assistant-bg': '#fff8e1',
                    '--sidebar-background': '#e8f5e8',
                    '--header-background': '#2e7d32',
                    '--code-background': '#e8f5e8',
                    '--code-border': '#c8e6c9'
                }
            },
            purple: {
                name: 'Roxo Real',
                icon: '💜',
                properties: {
                    '--primary-color': '#7b1fa2',
                    '--primary-dark': '#4a148c',
                    '--secondary-color': '#f3e5f5',
                    '--accent-color': '#ab47bc',
                    '--warning-color': '#ff8f00',
                    '--danger-color': '#d32f2f',
                    '--background-color': '#fafafa',
                    '--surface-color': '#f3e5f5',
                    '--card-background': '#ffffff',
                    '--text-color': '#4a148c',
                    '--text-muted': '#6a1b9a',
                    '--border-color': '#e1bee7',
                    '--input-background': '#ffffff',
                    '--button-background': '#7b1fa2',
                    '--button-text': '#ffffff',
                    '--shadow-color': 'rgba(123, 31, 162, 0.1)',
                    '--chat-user-bg': '#f3e5f5',
                    '--chat-assistant-bg': '#fce4ec',
                    '--sidebar-background': '#f3e5f5',
                    '--header-background': '#7b1fa2',
                    '--code-background': '#f3e5f5',
                    '--code-border': '#e1bee7'
                }
            }
        };

        this.currentTheme = 'light';
        this.transitionDuration = '0.3s';
        
        this.init();
    }

    init() {
        this.loadSavedTheme();
        this.addThemeStyles();
        this.createThemeSelector();
        this.bindEvents();
    }

    loadSavedTheme() {
        const saved = localStorage.getItem('mamute-theme');
        if (saved && this.themes[saved]) {
            this.currentTheme = saved;
        }
    }

    addThemeStyles() {
        const style = document.createElement('style');
        style.id = 'theme-styles';
        style.textContent = this.getThemeCSS();
        document.head.appendChild(style);
    }

    getThemeCSS() {
        return `
            /* Transições suaves para mudança de tema */
            * {
                transition: background-color ${this.transitionDuration}, 
                           border-color ${this.transitionDuration}, 
                           color ${this.transitionDuration},
                           box-shadow ${this.transitionDuration} !important;
            }

            /* Aplicar variáveis CSS */
            :root {
                ${this.getCSSVariables()}
            }

            /* Estilos gerais usando as variáveis */
            body {
                background-color: var(--background-color);
                color: var(--text-color);
            }

            .main-container {
                background-color: var(--background-color);
            }

            .sidebar {
                background-color: var(--sidebar-background);
                border-right: 1px solid var(--border-color);
            }

            .header {
                background: var(--header-background);
                border-bottom: 1px solid var(--border-color);
            }

            .card {
                background-color: var(--card-background);
                border: 1px solid var(--border-color);
                box-shadow: 0 2px 4px var(--shadow-color);
            }

            .form-control {
                background-color: var(--input-background);
                border: 1px solid var(--border-color);
                color: var(--text-color);
            }

            .form-control:focus {
                border-color: var(--primary-color);
                box-shadow: 0 0 0 0.2rem rgba(74, 144, 226, 0.25);
            }

            .btn-primary {
                background-color: var(--button-background);
                border-color: var(--button-background);
                color: var(--button-text);
            }

            .btn-primary:hover {
                background-color: var(--primary-dark);
                border-color: var(--primary-dark);
            }

            .btn-secondary {
                background-color: var(--surface-color);
                border-color: var(--border-color);
                color: var(--text-color);
            }

            .btn-success {
                background-color: var(--accent-color);
                border-color: var(--accent-color);
            }

            .btn-warning {
                background-color: var(--warning-color);
                border-color: var(--warning-color);
            }

            .btn-danger {
                background-color: var(--danger-color);
                border-color: var(--danger-color);
            }

            .text-muted {
                color: var(--text-muted) !important;
            }

            /* Chat messages */
            .message.user {
                background-color: var(--chat-user-bg);
                border-left: 4px solid var(--primary-color);
            }

            .message.assistant {
                background-color: var(--chat-assistant-bg);
                border-left: 4px solid var(--accent-color);
            }

            .message.system {
                background-color: var(--surface-color);
                border-left: 4px solid var(--text-muted);
            }

            /* Code blocks */
            pre, code {
                background-color: var(--code-background);
                border: 1px solid var(--code-border);
                color: var(--text-color);
            }

            /* Tables */
            .table {
                color: var(--text-color);
            }

            .table th {
                border-color: var(--border-color);
                background-color: var(--surface-color);
            }

            .table td {
                border-color: var(--border-color);
            }

            /* Modal */
            .modal-content {
                background-color: var(--card-background);
                color: var(--text-color);
            }

            .modal-header {
                border-bottom: 1px solid var(--border-color);
            }

            .modal-footer {
                border-top: 1px solid var(--border-color);
            }

            /* Theme selector */
            .theme-selector {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }

            .theme-toggle {
                background: var(--card-background);
                border: 1px solid var(--border-color);
                border-radius: 50%;
                width: 50px;
                height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                font-size: 1.5rem;
                box-shadow: 0 2px 8px var(--shadow-color);
                transition: transform 0.2s, box-shadow 0.2s;
            }

            .theme-toggle:hover {
                transform: scale(1.1);
                box-shadow: 0 4px 12px var(--shadow-color);
            }

            .theme-options {
                display: none;
                flex-direction: column;
                gap: 0.5rem;
                background: var(--card-background);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                padding: 1rem;
                box-shadow: 0 4px 16px var(--shadow-color);
                min-width: 180px;
            }

            .theme-options.show {
                display: flex;
            }

            .theme-option {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.5rem;
                border: none;
                background: transparent;
                border-radius: 6px;
                cursor: pointer;
                color: var(--text-color);
                transition: background-color 0.2s;
            }

            .theme-option:hover {
                background-color: var(--surface-color);
            }

            .theme-option.active {
                background-color: var(--primary-color);
                color: var(--button-text);
            }

            .theme-icon {
                font-size: 1.2rem;
            }

            .theme-name {
                font-weight: 500;
            }

            /* Indicators de status */
            .status-indicator {
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                margin-right: 0.5rem;
            }

            .status-online {
                background-color: var(--accent-color);
            }

            .status-offline {
                background-color: var(--text-muted);
            }

            .status-error {
                background-color: var(--danger-color);
            }

            /* Scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
            }

            ::-webkit-scrollbar-track {
                background: var(--surface-color);
            }

            ::-webkit-scrollbar-thumb {
                background: var(--border-color);
                border-radius: 4px;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: var(--text-muted);
            }

            /* Search suggestions */
            .search-suggestions {
                background: var(--card-background);
                border: 1px solid var(--border-color);
                box-shadow: 0 4px 12px var(--shadow-color);
            }

            .search-suggestion:hover {
                background-color: var(--surface-color);
            }

            /* Chart containers */
            .chart-container {
                background: var(--card-background);
                border: 1px solid var(--border-color);
            }

            /* File upload zones */
            .drop-zone {
                border: 2px dashed var(--border-color);
                background: var(--surface-color);
            }

            .drop-zone:hover,
            .drop-zone.drag-over {
                border-color: var(--primary-color);
                background-color: var(--chat-user-bg);
            }

            /* Document items */
            .document-item {
                background: var(--card-background);
                border: 1px solid var(--border-color);
            }

            .document-item:hover {
                box-shadow: 0 4px 8px var(--shadow-color);
            }

            /* Progress bars */
            .progress {
                background-color: var(--surface-color);
            }

            .progress-fill {
                background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
            }
        `;
    }

    getCSSVariables() {
        const theme = this.themes[this.currentTheme];
        return Object.entries(theme.properties)
            .map(([key, value]) => `${key}: ${value};`)
            .join('\n                ');
    }

    createThemeSelector() {
        const selector = document.createElement('div');
        selector.className = 'theme-selector';
        selector.innerHTML = `
            <button class="theme-toggle" id="themeToggle" title="Alterar Tema">
                ${this.themes[this.currentTheme].icon}
            </button>
            <div class="theme-options" id="themeOptions">
                ${Object.entries(this.themes).map(([key, theme]) => `
                    <button class="theme-option ${key === this.currentTheme ? 'active' : ''}" 
                            data-theme="${key}">
                        <span class="theme-icon">${theme.icon}</span>
                        <span class="theme-name">${theme.name}</span>
                    </button>
                `).join('')}
            </div>
        `;

        document.body.appendChild(selector);
    }

    bindEvents() {
        const themeToggle = document.getElementById('themeToggle');
        const themeOptions = document.getElementById('themeOptions');

        if (themeToggle) {
            themeToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                themeOptions.classList.toggle('show');
            });
        }

        // Fechar menu ao clicar fora
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.theme-selector')) {
                themeOptions.classList.remove('show');
            }
        });

        // Event listeners para opções de tema
        document.addEventListener('click', (e) => {
            if (e.target.closest('.theme-option')) {
                const themeKey = e.target.closest('.theme-option').dataset.theme;
                this.setTheme(themeKey);
                themeOptions.classList.remove('show');
            }
        });

        // Atalho de teclado para trocar tema (Ctrl + T)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 't') {
                e.preventDefault();
                this.cycleTheme();
            }
        });
    }

    setTheme(themeKey) {
        if (!this.themes[themeKey]) return;

        this.currentTheme = themeKey;
        
        // Atualizar CSS
        this.updateThemeCSS();
        
        // Atualizar botão
        this.updateThemeButton();
        
        // Atualizar opções ativas
        this.updateActiveOption();
        
        // Salvar preferência
        localStorage.setItem('mamute-theme', themeKey);

        // Disparar evento customizado
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: themeKey, properties: this.themes[themeKey].properties }
        }));

        console.log(`Tema alterado para: ${this.themes[themeKey].name}`);
    }

    updateThemeCSS() {
        const styleElement = document.getElementById('theme-styles');
        if (styleElement) {
            styleElement.textContent = this.getThemeCSS();
        }
    }

    updateThemeButton() {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.textContent = this.themes[this.currentTheme].icon;
            themeToggle.title = `Tema Atual: ${this.themes[this.currentTheme].name}`;
        }
    }

    updateActiveOption() {
        document.querySelectorAll('.theme-option').forEach(option => {
            option.classList.remove('active');
            if (option.dataset.theme === this.currentTheme) {
                option.classList.add('active');
            }
        });
    }

    cycleTheme() {
        const themeKeys = Object.keys(this.themes);
        const currentIndex = themeKeys.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % themeKeys.length;
        this.setTheme(themeKeys[nextIndex]);
    }

    // Método para obter cores do tema atual (para gráficos)
    getCurrentThemeColors() {
        const theme = this.themes[this.currentTheme];
        return {
            primary: theme.properties['--primary-color'],
            secondary: theme.properties['--secondary-color'],
            accent: theme.properties['--accent-color'],
            background: theme.properties['--background-color'],
            text: theme.properties['--text-color'],
            border: theme.properties['--border-color']
        };
    }

    // Método para aplicar tema aos gráficos Chart.js
    updateChartDefaults() {
        if (typeof Chart !== 'undefined') {
            const colors = this.getCurrentThemeColors();
            
            Chart.defaults.color = colors.text;
            Chart.defaults.borderColor = colors.border;
            Chart.defaults.backgroundColor = colors.background;
            Chart.defaults.plugins.legend.labels.color = colors.text;
            Chart.defaults.scales.category.grid.color = colors.border;
            Chart.defaults.scales.linear.grid.color = colors.border;
            Chart.defaults.scales.category.ticks.color = colors.text;
            Chart.defaults.scales.linear.ticks.color = colors.text;
        }
    }
}

// Inicializar gerenciador de temas
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
    
    // Atualizar gráficos quando tema mudar
    window.addEventListener('themeChanged', () => {
        if (window.themeManager) {
            window.themeManager.updateChartDefaults();
            
            // Recriar gráficos se existirem
            if (window.mamuteCharts) {
                window.mamuteCharts.updateChartsTheme();
            }
        }
    });
});

// Exportar para uso global
window.ThemeManager = ThemeManager;