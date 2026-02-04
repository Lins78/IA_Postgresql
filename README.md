# IA conectada ao PostgreSQL

Este projeto implementa um sistema de Inteligência Artificial conectada ao PostgreSQL, oferecendo conversas naturais, análise de dados e busca semântica.

## 🚀 Características

- **Chat Inteligente**: Converse naturalmente com a IA sobre seus dados
- **Busca Semântica**: Encontre documentos relevantes usando embeddings
- **Análise de Dados**: Analise automaticamente tabelas do PostgreSQL
- **Interface Web**: Interface amigável com Streamlit
- **Armazenamento**: Histórico de conversas e documentos no PostgreSQL
- **Modular**: Arquitetura limpa e extensível

## 📋 Pré-requisitos

- Python 3.11+
- PostgreSQL 12+
- Conta OpenAI (para API de IA e embeddings)

## 🛠️ Instalação

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd IA_Postgresql
   ```

2. **Crie um ambiente virtual**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\\Scripts\\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o ambiente**
   ```bash
   # Copie o arquivo de exemplo
   cp .env.example .env
   
   # Edite o arquivo .env com suas configurações
   ```

5. **Configure o PostgreSQL**
   - Crie um banco de dados para o projeto
   - Atualize as credenciais no arquivo `.env`

## ⚙️ Configuração

Edite o arquivo `.env` com suas configurações:

```env
# API OpenAI
OPENAI_API_KEY=sua_chave_aqui

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ia_database
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha

# Configurações da IA
MAX_TOKENS=4000
TEMPERATURE=0.7
DEBUG=True
```

## 🚀 Como Usar

### Execução Básica

```bash
python main.py
```

### Interface Web (Streamlit)

```bash
streamlit run examples/streamlit_app.py
```

Acesse: http://localhost:8501

### Exemplos de Código

```python
from main import IAPostgreSQL

# Inicializar sistema
ia = IAPostgreSQL()
ia.setup_database()

# Iniciar conversa
session_id = ia.start_conversation("meu_usuario")

# Conversar com a IA
response = ia.chat("Olá! Como você pode me ajudar?", session_id)
print(response["response"])

# Adicionar documento
doc_id = ia.add_document(
    title="Manual PostgreSQL",
    content="PostgreSQL é um banco de dados...",
    metadata={"categoria": "documentacao"}
)

# Analisar tabela
analysis = ia.analyze_table("minha_tabela")
print(f"Tabela tem {analysis['total_rows']} linhas")
```

## 📁 Estrutura do Projeto

```
IA_Postgresql/
├── src/
│   ├── ai/                 # Módulos de IA
│   │   ├── agent.py        # Agente principal
│   │   ├── chat.py         # Gerenciador de chat
│   │   └── embeddings.py   # Gerenciador de embeddings
│   ├── database/           # Módulos de banco
│   │   ├── connection.py   # Conexão PostgreSQL
│   │   └── models.py       # Modelos de dados
│   └── utils/              # Utilitários
│       ├── config.py       # Configurações
│       └── logger.py       # Sistema de logs
├── examples/               # Exemplos de uso
│   ├── exemplo_basico.py   # Exemplo básico
│   └── streamlit_app.py    # Interface web
├── main.py                 # Arquivo principal
├── requirements.txt        # Dependências
└── .env.example           # Exemplo de configuração
```

## 🎯 Funcionalidades

### 1. Chat com IA
- Conversas naturais sobre dados
- Contexto de conversa mantido
- Histórico armazenado no banco
- Estatísticas de uso

### 2. Busca Semântica
- Adicionar documentos com embeddings
- Busca por similaridade semântica
- Metadados e categorização
- Integração com chat

### 3. Análise de Dados
- Análise automática de tabelas
- Informações de estrutura
- Estatísticas básicas
- Amostras de dados

### 4. Interface Web
- Chat interativo
- Gerenciamento de documentos
- Dashboard com estatísticas
- Visualizações com Plotly

## 🔧 Exemplos de Uso

### Exemplo 1: Chat Simples
```bash
python examples/exemplo_basico.py
```

### Exemplo 2: Interface Web
```bash
streamlit run examples/streamlit_app.py
```

## 📊 Banco de Dados

O sistema cria automaticamente as seguintes tabelas:

- `conversations`: Histórico de conversas
- `user_sessions`: Sessões de usuários
- `documents`: Documentos com embeddings
- `queries`: Queries executadas
- `ai_models`: Configurações de modelos

## 🛡️ Segurança

- Senhas armazenadas em variáveis de ambiente
- Conexões seguras com PostgreSQL
- Validação de entradas
- Sistema de logs

## 🔍 Troubleshooting

### Erro de Conexão PostgreSQL
```bash
# Verificar se o PostgreSQL está rodando
sudo systemctl status postgresql

# Verificar configurações no .env
```

### Erro de API OpenAI
```bash
# Verificar se a chave está correta
# Verificar saldo da conta OpenAI
```

### Erro de Dependências
```bash
# Reinstalar dependências
pip install -r requirements.txt --upgrade
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📞 Suporte

Para dúvidas e suporte:
- Abra uma issue no GitHub
- Consulte a documentação dos componentes
- Verifique os logs do sistema

## 🎉 Próximos Passos

- [ ] Integração com mais modelos de IA
- [ ] API REST
- [ ] Autenticação de usuários
- [ ] Cache de embeddings
- [ ] Visualizações avançadas
- [ ] Exportação de dados