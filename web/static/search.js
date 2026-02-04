// JavaScript para Sistema de Busca Inteligente
class IntelligentSearch {
    constructor() {
        this.currentQuery = '';
        this.isSearching = false;
        this.suggestions = [];
        this.stats = {};
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSearchStats();
    }

    setupEventListeners() {
        const searchInput = document.getElementById('searchQuery');
        const searchButton = document.getElementById('searchButton');
        const searchType = document.getElementById('searchType');
        const contentType = document.getElementById('contentType');
        const minSimilarity = document.getElementById('minSimilarity');
        const similarityValue = document.getElementById('similarityValue');
        const maxResults = document.getElementById('maxResults');

        // Busca principal
        if (searchButton) {
            searchButton.addEventListener('click', () => {
                this.performSearch();
            });
        }

        if (searchInput) {
            // Busca ao pressionar Enter
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch();
                }
            });

            // Sugestões em tempo real
            searchInput.addEventListener('input', (e) => {
                this.handleSearchInput(e.target.value);
            });

            // Esconder sugestões ao perder foco
            searchInput.addEventListener('blur', () => {
                setTimeout(() => this.hideSuggestions(), 200);
            });
        }

        // Atualizar valor de similaridade
        if (minSimilarity && similarityValue) {
            minSimilarity.addEventListener('input', (e) => {
                similarityValue.textContent = e.target.value;
            });
        }

        // Auto-busca quando filtros mudam
        [searchType, contentType, minSimilarity, maxResults].forEach(element => {
            if (element) {
                element.addEventListener('change', () => {
                    if (this.currentQuery) {
                        this.performSearch();
                    }
                });
            }
        });
    }

    async handleSearchInput(query) {
        this.currentQuery = query;

        if (query.length > 2) {
            // Buscar sugestões
            await this.loadSuggestions(query);
            this.showSuggestions();
        } else {
            this.hideSuggestions();
        }
    }

    async loadSuggestions(query) {
        try {
            const response = await fetch(`/search/suggestions?q=${encodeURIComponent(query)}&limit=5`);
            
            if (response.ok) {
                const data = await response.json();
                this.suggestions = data.suggestions;
            } else {
                this.suggestions = [];
            }
        } catch (error) {
            console.error('Erro ao carregar sugestões:', error);
            this.suggestions = [];
        }
    }

    showSuggestions() {
        const container = document.getElementById('searchSuggestions');
        if (!container || this.suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }

        container.innerHTML = '';
        
        this.suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.textContent = suggestion;
            
            item.addEventListener('click', () => {
                document.getElementById('searchQuery').value = suggestion;
                this.currentQuery = suggestion;
                this.hideSuggestions();
                this.performSearch();
            });
            
            container.appendChild(item);
        });

        container.style.display = 'block';
    }

    hideSuggestions() {
        const container = document.getElementById('searchSuggestions');
        if (container) {
            container.style.display = 'none';
        }
    }

    async performSearch() {
        const query = document.getElementById('searchQuery').value.trim();
        
        if (!query) {
            this.showError('Digite algo para buscar');
            return;
        }

        if (this.isSearching) {
            return; // Evitar múltiplas buscas simultâneas
        }

        this.isSearching = true;
        this.currentQuery = query;
        
        // Mostrar loading
        this.showLoading();
        
        try {
            const searchRequest = this.buildSearchRequest();
            
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(searchRequest)
            });

            if (response.ok) {
                const results = await response.json();
                this.displayResults(results);
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Erro na busca');
            }

        } catch (error) {
            console.error('Erro na busca:', error);
            this.showError('Erro de conexão com o servidor');
        } finally {
            this.isSearching = false;
            this.hideLoading();
        }
    }

    buildSearchRequest() {
        const searchType = document.getElementById('searchType').value;
        const contentType = document.getElementById('contentType').value;
        const minSimilarity = parseFloat(document.getElementById('minSimilarity').value);
        const maxResults = parseInt(document.getElementById('maxResults').value);

        const request = {
            query: this.currentQuery,
            search_type: searchType,
            min_similarity: minSimilarity,
            max_results: maxResults
        };

        if (contentType) {
            request.content_type = contentType;
        }

        return request;
    }

    displayResults(data) {
        const container = document.getElementById('searchResults');
        if (!container) return;

        const { results, total_results, query, search_type } = data;

        if (total_results === 0) {
            container.innerHTML = `
                <div class="no-results">
                    <h3>🔍 Nenhum resultado encontrado</h3>
                    <p>Tente usar palavras-chave diferentes ou ajustar os filtros.</p>
                    <ul>
                        <li>Verifique a ortografia das palavras</li>
                        <li>Use termos mais gerais</li>
                        <li>Reduza a similaridade mínima</li>
                        <li>Experimente o modo de busca "Híbrida"</li>
                    </ul>
                </div>
            `;
            return;
        }

        let html = `
            <div class="results-header">
                <h3>📊 Resultados da Busca</h3>
                <p>Encontrados <strong>${total_results}</strong> resultado(s) para "<strong>${query}</strong>" 
                   usando busca <strong>${this.getSearchTypeLabel(search_type)}</strong></p>
            </div>
            <div class="results-list">
        `;

        results.forEach((result, index) => {
            html += this.renderResultItem(result, index);
        });

        html += '</div>';
        container.innerHTML = html;
    }

    renderResultItem(result, index) {
        const similarity = (result.similarity * 100).toFixed(1);
        const timestamp = result.timestamp ? new Date(result.timestamp).toLocaleString('pt-BR') : null;
        const contentTypeIcon = this.getContentTypeIcon(result.content_type);
        const truncatedContent = this.truncateText(result.content, 200);

        return `
            <div class="result-item" data-index="${index}">
                <div class="result-title">
                    ${contentTypeIcon} ${result.title}
                </div>
                <div class="result-content">
                    ${this.highlightQuery(truncatedContent, this.currentQuery)}
                </div>
                <div class="result-meta">
                    <span class="result-similarity">${similarity}%</span>
                    <span class="result-type">${this.getContentTypeLabel(result.content_type)}</span>
                    ${result.source ? `<span class="result-source">📍 ${result.source}</span>` : ''}
                    ${result.category ? `<span class="result-category">🏷️ ${result.category}</span>` : ''}
                    ${timestamp ? `<span class="result-timestamp">🕐 ${timestamp}</span>` : ''}
                </div>
                ${result.metadata ? this.renderMetadata(result.metadata) : ''}
            </div>
        `;
    }

    renderMetadata(metadata) {
        if (!metadata || Object.keys(metadata).length === 0) {
            return '';
        }

        let html = '<div class="result-metadata"><strong>Metadados:</strong> ';
        const items = [];
        
        Object.entries(metadata).forEach(([key, value]) => {
            if (key !== 'row_data') { // Não mostrar dados brutos de linha
                items.push(`${key}: ${value}`);
            }
        });

        html += items.join(', ') + '</div>';
        return html;
    }

    highlightQuery(text, query) {
        if (!query) return text;
        
        const words = query.toLowerCase().split(/\s+/);
        let highlightedText = text;

        words.forEach(word => {
            if (word.length > 2) {
                const regex = new RegExp(`(${word})`, 'gi');
                highlightedText = highlightedText.replace(regex, '<mark>$1</mark>');
            }
        });

        return highlightedText;
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) {
            return text;
        }
        return text.substr(0, maxLength) + '...';
    }

    getSearchTypeLabel(searchType) {
        const labels = {
            'hybrid': 'Híbrida',
            'semantic': 'Semântica',
            'keyword': 'Palavras-chave',
            'sql': 'SQL'
        };
        return labels[searchType] || searchType;
    }

    getContentTypeIcon(contentType) {
        const icons = {
            'document': '📄',
            'conversation': '💬',
            'query_result': '📊',
            'log_entry': '📝',
            'table_data': '🗃️'
        };
        return icons[contentType] || '📄';
    }

    getContentTypeLabel(contentType) {
        const labels = {
            'document': 'Documento',
            'conversation': 'Conversa',
            'query_result': 'Resultado SQL',
            'log_entry': 'Log',
            'table_data': 'Dados de Tabela'
        };
        return labels[contentType] || contentType;
    }

    showLoading() {
        const container = document.getElementById('searchResults');
        if (container) {
            container.innerHTML = `
                <div class="search-loading">
                    <div class="loading-spinner"></div>
                    <h3>🔍 Buscando...</h3>
                    <p>Analisando documentos, conversas e dados...</p>
                </div>
            `;
        }

        const button = document.getElementById('searchButton');
        if (button) {
            button.disabled = true;
            button.innerHTML = '⏳ Buscando...';
        }
    }

    hideLoading() {
        const button = document.getElementById('searchButton');
        if (button) {
            button.disabled = false;
            button.innerHTML = '🔍 Buscar';
        }
    }

    showError(message) {
        const container = document.getElementById('searchResults');
        if (container) {
            container.innerHTML = `
                <div class="search-error">
                    <h3>❌ Erro na Busca</h3>
                    <p>${message}</p>
                    <button onclick="location.reload()" class="btn btn-secondary">🔄 Tentar Novamente</button>
                </div>
            `;
        }
    }

    async loadSearchStats() {
        try {
            const response = await fetch('/search/stats');
            
            if (response.ok) {
                this.stats = await response.json();
                this.displayStats();
            }
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
        }
    }

    displayStats() {
        const container = document.getElementById('searchStats');
        if (!container || !this.stats) return;

        const {
            total_documents = 0,
            total_conversations = 0,
            total_query_logs = 0,
            cache_size = 0,
            last_index_update
        } = this.stats;

        const totalContent = total_documents + total_conversations + total_query_logs;
        const lastUpdate = last_index_update ? 
            new Date(last_index_update).toLocaleString('pt-BR') : 
            'Nunca';

        container.innerHTML = `
            <h3>📈 Estatísticas do Sistema de Busca</h3>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number">${totalContent}</div>
                    <div class="stat-label">Total de Conteúdo</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${total_documents}</div>
                    <div class="stat-label">Documentos</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${total_conversations}</div>
                    <div class="stat-label">Conversas</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${total_query_logs}</div>
                    <div class="stat-label">Logs de Query</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${cache_size}</div>
                    <div class="stat-label">Itens em Cache</div>
                </div>
                <div class="stat-item">
                    <div class="stat-text">${lastUpdate}</div>
                    <div class="stat-label">Última Atualização</div>
                </div>
            </div>
        `;
    }
}

// Adicionar estilos CSS dinamicamente
const styles = `
    .search-loading {
        text-align: center;
        padding: 3rem;
        color: #667eea;
    }

    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .search-error {
        text-align: center;
        padding: 3rem;
        color: #dc3545;
    }

    .no-results {
        text-align: center;
        padding: 3rem;
        color: #666;
    }

    .no-results ul {
        text-align: left;
        max-width: 400px;
        margin: 1rem auto;
    }

    .no-results li {
        margin: 0.5rem 0;
    }

    .results-header {
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e9ecef;
    }

    .results-header h3 {
        color: #667eea;
        margin-bottom: 0.5rem;
    }

    .result-metadata {
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid #f0f0f0;
        font-size: 0.8rem;
        color: #888;
    }

    mark {
        background: #fff3cd;
        padding: 0.1rem 0.2rem;
        border-radius: 3px;
        font-weight: 600;
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }

    .stat-item {
        text-align: center;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
    }

    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }

    .stat-text {
        font-size: 0.9rem;
        font-weight: 600;
        color: #333;
    }

    .stat-label {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.2rem;
    }
`;

// Adicionar estilos ao DOM
const styleSheet = document.createElement('style');
styleSheet.textContent = styles;
document.head.appendChild(styleSheet);

// Inicializar busca inteligente quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('searchQuery')) {
        window.intelligentSearch = new IntelligentSearch();
    }
});

window.IntelligentSearch = IntelligentSearch;