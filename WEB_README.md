# 🐘 Mamute - IA PostgreSQL Web

## 🌐 Aplicação Web Completa

O **Mamute** agora está disponível através de navegadores web com uma interface moderna e completa! 

## 🚀 Como Iniciar o Servidor Web

### Método 1: Script Automático
```bash
python start_web.py
```
- ✅ Inicia o servidor automaticamente
- ✅ Abre o navegador
- ✅ URL: http://localhost:8000

### Método 2: Manual
```bash
python web_app.py
```
ou
```bash
uvicorn web_app:app --host 0.0.0.0 --port 8000 --reload
```

## 🎯 Funcionalidades Web

### 📊 Dashboard Principal
- **Status do Sistema**: Monitoramento em tempo real
- **Conexão PostgreSQL**: Verificação de conectividade
- **Consultas SQL**: Execução direta no navegador
- **Informações do Banco**: Host, database, status

### 💬 Chat Interativo
- **Interface Moderna**: Design responsivo e elegante
- **Tempo Real**: Conversas fluidas com Mamute
- **Contexto**: Mantém histórico da conversa
- **Documentos Relevantes**: Busca automática
- **Estatísticas**: Tokens e tempo de resposta

### 🔧 API RESTful
Endpoints disponíveis:
- `GET /` - Dashboard principal
- `GET /chat` - Interface de chat
- `POST /session/start` - Iniciar sessão
- `POST /chat` - Conversar com Mamute
- `POST /query` - Executar consultas SQL
- `POST /documents` - Adicionar documentos
- `GET /health` - Status do sistema
- `GET /docs` - Documentação automática

## 🎨 Interface Moderna

### Características do Design:
- **Responsiva**: Funciona em desktop, tablet e mobile
- **Gradientes**: Visual moderno com cores do Mamute
- **Cards**: Layout organizado em cartões
- **Animações**: Transições suaves
- **Ícones**: Emojis intuitivos para navegação

### Tecnologias Utilizadas:
- **Backend**: FastAPI + Uvicorn
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: CSS Grid, Flexbox, Gradientes
- **API**: RESTful com documentação automática
- **WebSockets**: Suporte para chat em tempo real

## 📱 Compatibilidade

### Navegadores Suportados:
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers

### Recursos Disponíveis:
- ✅ Chat responsivo
- ✅ Consultas SQL diretas
- ✅ Dashboard de status
- ✅ API documentada
- ✅ Interface multilíngue (PT-BR)

## 🔒 Segurança

### Medidas Implementadas:
- **Consultas SQL**: Apenas SELECT permitido
- **CORS**: Configurado para desenvolvimento
- **Validação**: Pydantic para entrada de dados
- **Error Handling**: Tratamento robusto de erros

## 🧪 Testar a API

Execute o script de teste:
```bash
python test_web_api.py
```

### Verificações do Teste:
- ✅ Health check do sistema
- ✅ Criação de sessão
- ✅ Funcionalidade de chat
- ✅ Execução de consultas SQL

## 📖 Documentação da API

Acesse a documentação interativa em:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ Configuração

### Arquivo .env:
```env
AI_NAME=Mamute
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ia_database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres@
OPENAI_API_KEY=your_openai_api_key_here
```

### Para OpenAI (Opcional):
- Configure uma chave válida da OpenAI para chat completo
- Sem a chave, as funcionalidades de banco funcionam normalmente

## 📁 Estrutura dos Arquivos Web

```
web/
├── static/
│   ├── mamute.css      # Estilos CSS modernos
│   └── mamute.js       # JavaScript para interatividade
└── templates/          # (Reservado para templates Jinja2)

web_app.py              # Aplicação FastAPI principal
start_web.py            # Script de inicialização
test_web_api.py         # Testes automatizados
```

## 🎉 Resultado

O **Mamute** agora é uma aplicação web completa e moderna, acessível através de qualquer navegador, com:

- 🎯 **Dashboard intuitivo**
- 💬 **Chat em tempo real**
- 📊 **Execução de consultas**
- 📖 **API bem documentada**
- 🎨 **Interface responsiva**
- 🔧 **Fácil configuração**

**Acesse http://localhost:8000 e comece a usar o Mamute no seu navegador!** 🐘✨