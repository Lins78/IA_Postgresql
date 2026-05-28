📋 INSTRUÇÕES PARA INTEGRAÇÃO COM POSTGRESQL
==============================================

✅ POSTGRESQL DETECTADO E FUNCIONANDO!
   📍 Local: C:\PostgreSql\bin
   📊 Versão: PostgreSQL 9.4.26
   🟢 Status: Rodando

🔧 PRÓXIMOS PASSOS PARA INTEGRAÇÃO:

1️⃣ CONFIGURAR CREDENCIAIS
   Execute: python configure_credentials.py
   
   Será solicitado:
   - Host [localhost] ← Pressione Enter para manter
   - Porta [5432] ← Pressione Enter para manter  
   - Usuário [postgres] ← Pressione Enter para manter
   - Senha: ← Digite a senha do seu PostgreSQL
   - Nome do banco [ia_database] ← Pressione Enter para manter
   - OpenAI API Key ← Opcional por enquanto

2️⃣ TESTAR CONEXÃO
   Execute: python test_connection.py
   
3️⃣ CONFIGURAR BANCO COMPLETO  
   Execute: python setup_postgres.py
   (Cria banco e tabelas automaticamente)

4️⃣ EXECUTAR SISTEMA
   Escolha uma opção:
   
   • Interface Web (Recomendado):
     streamlit run examples/streamlit_app.py
   
   • Modo Console:
     python main.py
   
   • Exemplos:
     python examples/exemplo_basico.py

🆘 EM CASO DE PROBLEMAS:

❌ Erro de Autenticação:
   - Verifique a senha do PostgreSQL
   - Tente: postgres / admin / root

❌ Erro de Conexão:
   - Verifique se PostgreSQL está rodando
   - Execute: net start postgresql

❌ Banco não existe:
   - Será criado automaticamente no setup

💡 DICAS:

• Para PostgreSQL 9.4, a senha padrão geralmente é:
  - "postgres" (mais comum)
  - Senha definida durante instalação
  - Vazia (sem senha)

• Se não lembrar a senha, pode redefinir através do:
  C:\PostgreSql\bin\pg_ctl.exe

• O sistema criará automaticamente:
  - Banco de dados: ia_database
  - Todas as tabelas necessárias
  - Índices e relações

🎯 COMANDO RÁPIDO:
Execute: run_new.bat
(Menu interativo com todas as opções)

🚀 DEPOIS DA CONFIGURAÇÃO:
O sistema oferecerá:
✓ Chat inteligente com IA
✓ Busca semântica de documentos
✓ Análise automática de dados
✓ Interface web moderna
✓ Dashboard com estatísticas