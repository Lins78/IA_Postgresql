@echo off
title Configuração Definitiva 24h - Mamute
chcp 65001 >nul
echo.
echo ████████████████████████████████████████████████████████████████
echo ██                                                            ██
echo ██     🚀 CONFIGURAÇÃO DEFINITIVA 24H - MAMUTE             ██
echo ██     Nunca mais desconectar quando fechar o notebook       ██
echo ██                                                            ██  
echo ████████████████████████████████████████████████████████████████
echo.

cd /d "%~dp0"

echo 🎯 ESCOLHA UMA SOLUÇÃO:
echo.
echo 1. 🏠 Serviço Windows (MELHOR - roda sempre)
echo 2. 🕐 Tarefa Agendada (alternativa)  
echo 3. 💻 Configurar notebook para não hibernar
echo 4. ☁️ Solução Cloud/VPS (acesso remoto real)
echo 5. 📊 Verificar status atual
echo.

set /p choice="💡 Digite sua escolha (1-5): "

if "%choice%"=="1" goto servico_windows
if "%choice%"=="2" goto tarefa_agendada  
if "%choice%"=="3" goto configurar_energia
if "%choice%"=="4" goto solucao_cloud
if "%choice%"=="5" goto verificar_status
echo ❌ Opção inválida!
goto end

:servico_windows
setlocal enableextensions enabledelayedexpansion
echo.
echo 🏠 INSTALANDO COMO SERVIÇO WINDOWS...

:: Validar se o instalador do serviço existe
if not exist "%~dp0install_mamute_service.bat" goto missing_installer

:: Verificar se está rodando como administrador
net session >nul 2>&1
if %errorlevel% neq 0 goto need_admin

echo ✅ Privilégios administrativos confirmados
echo.
echo 🚀 Executando instalação do serviço...
echo.

call "%~dp0install_mamute_service.bat"
set "svc_err=%errorlevel%"
if "%svc_err%"=="0" goto install_ok
goto install_fail

:install_ok
echo.
echo ✅ SERVIÇO INSTALADO COM SUCESSO!
echo 🎉 Sua IA agora roda 24h automaticamente!
echo.
echo 📋 VERIFICAR STATUS:
echo    Comando: sc query MamuteIA24h
echo.
sc query MamuteIA24h
echo.
pause
endlocal
goto end

:install_fail
echo.
echo ❌ Houve um erro na instalação
echo 📋 Verifique os logs em: logs\service.log
echo Código de erro: %svc_err%
echo.
pause
endlocal
goto end

:missing_installer
echo ❌ Arquivo install_mamute_service.bat não encontrado nesta pasta.
echo 📁 Caminho atual: %~dp0
echo 💡 Execute este .bat a partir da pasta completa do projeto (IA_Postgresql).
echo.
pause
endlocal
goto end

:need_admin
echo ❌ ERRO: Execute como Administrador!
echo.
echo 👉 Clique com botão direito no arquivo e escolha "Executar como administrador"
echo.
pause
endlocal
goto end

:tarefa_agendada  
echo.
echo 🕐 CRIANDO TAREFA AGENDADA...
schtasks /create /tn "MamuteIA24h" /tr "\"%~dp0mamute_definitivo_sempre_online.py\"" /sc onstart /ru System /f >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Tarefa criada! Mamute iniciará com Windows
    echo 🚀 Testando agora...
    start /b python mamute_definitivo_sempre_online.py
) else (
    echo ❌ Execute como administrador
)
goto end

:configurar_energia
echo.
echo 💻 CONFIGURANDO ECONOMIA DE ENERGIA...
echo.
echo 🔧 Alterando configurações para manter sistema ativo:
echo.

:: Configurar para não hibernar quando fechar a tampa
powercfg /setacvalueindex SCHEME_CURRENT 4f971e89-eebd-4455-a8de-9e59040e7347 5ca83367-6e45-459f-a27b-476b1d01c936 0
powercfg /setdcvalueindex SCHEME_CURRENT 4f971e89-eebd-4455-a8de-9e59040e7347 5ca83367-6e45-459f-a27b-476b1d01c936 0

:: Aplicar configurações
powercfg /setactive SCHEME_CURRENT

echo ✅ Configurações aplicadas:
echo    • Fechar tampa: NÃO hibernar
echo    • Sistema: Continuar rodando
echo.  
echo 🚀 Iniciando Mamute...
start /b python mamute_definitivo_sempre_online.py
goto end

:solucao_cloud
echo.
echo ☁️  SOLUÇÃO CLOUD/VPS - ACESSO REMOTO REAL 24H
echo.
echo 💡 Para acesso verdadeiramente 24h de qualquer lugar:
echo.
echo 🌟 OPÇÕES CLOUD GRATUITAS/BARATAS:
echo.
echo 1. 🆓 Oracle Cloud - Sempre gratuito
echo    • 1 instância VM gratuita para sempre
echo    • 1GB RAM, 1 CPU virtual
echo    • Suficiente para Mamute
echo.
echo 2. 💰 VPS Contabo - €4.99/mês  
echo    • 4GB RAM, 2 CPU
echo    • Muito poder para IA
echo.
echo 3. 🌐 DigitalOcean - $6/mês
echo    • 1GB RAM, 1 CPU
echo    • Interface amigável
echo.
echo 📋 COMO IMPLEMENTAR:
echo    1. Criar conta no provedor escolhido
echo    2. Instalar Ubuntu 22.04 LTS
echo    3. Copiar este projeto para lá
echo    4. Configurar HTTPS + domínio
echo    5. IA funcionará 24h real!
echo.
echo 💡 Quer que eu crie um guia detalhado? (s/n)
set /p guide="Resposta: "
if /i "%guide%"=="s" call :criar_guia_cloud
goto end

:verificar_status
echo.
echo 📊 VERIFICANDO STATUS ATUAL...
echo.

:: Verificar se o serviço está instalado
sc query MamuteIA24h >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ SERVIÇO INSTALADO E RODANDO!
    echo.
    echo 📋 Detalhes do serviço:
    sc query MamuteIA24h
    echo.
    echo 📊 Processos Python relacionados:
    tasklist /fi "imagename eq python.exe" | findstr python
    echo.
    echo 🌐 Testando conectividade:
    echo    • Porto local 8001: 
    netstat -an | findstr ":8001"
    echo.
    echo 📁 Logs recentes:
    if exist "logs\service.log" (
        echo    • Últimas linhas do log:
        powershell Get-Content logs\service.log -Tail 5
    )
) else (
    echo ❌ SERVIÇO NÃO INSTALADO
    echo.
    echo 💡 Execute a opção 1 para instalar como serviço
    echo.
    echo 🔍 Verificando processos Python ativos:
    tasklist /fi "imagename eq python.exe" | findstr python || echo    • Nenhum processo Python encontrado
)

echo.
echo 💻 Para verificar se está acessível:
echo    • Local: http://localhost:8001
echo    • Rede: http://192.168.1.70:8001
echo    • IP atual: 
ipconfig | findstr "IPv4"
echo.
goto end

:criar_guia_cloud
echo.
echo 📝 Criando guia detalhado para solução cloud...
(
echo # 🚀 Guia Definitivo - Mamute na Cloud 24h
echo.
echo ## ☁️  Opção 1: Oracle Cloud ^(GRATUITO PARA SEMPRE^)
echo.
echo ### 1. Criar conta Oracle Cloud
echo ```
echo 1. Acesse: https://cloud.oracle.com
echo 2. Click "Start for free"  
echo 3. Complete cadastro ^(precisa cartão, mas não cobra^)
echo 4. Verificar email
echo ```
echo.
echo ### 2. Criar instância VM
echo ```
echo 1. No painel: Compute ^> Instances
echo 2. Create Instance
echo 3. Configurações:
echo    - Name: mamute-ia
echo    - Image: Ubuntu 22.04
echo    - Shape: VM.Standard.E2.1.Micro ^(ALWAYS FREE^)
echo    - RAM: 1GB ^(suficiente^)
echo 4. Add SSH key ou create novo
echo 5. Create
echo ```
echo.
echo ### 3. Configurar firewall
echo ```
echo 1. Na instância: Subnet ^> Security List
echo 2. Add Ingress Rule:
echo    - Source: 0.0.0.0/0
echo    - Destination Port: 8001,22,80,443
echo 3. Save
echo ```
echo.
echo ### 4. Conectar e instalar
echo ```bash
echo # Conectar via SSH
echo ssh ubuntu@^<IP-DA-INSTANCIA^>
echo.
echo # Atualizar sistema  
echo sudo apt update ^&^& sudo apt upgrade -y
echo.
echo # Instalar Python e dependências
echo sudo apt install python3-pip git postgresql postgresql-contrib nginx -y
echo.
echo # Baixar projeto
echo git clone ^<SEU-REPO-GITHUB^> mamute
echo cd mamute
echo.
echo # Instalar dependências Python
echo pip3 install -r requirements.txt
echo.
echo # Configurar PostgreSQL
echo sudo -u postgres createdb ia_database
echo sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres@';"
echo.
echo # Configurar como serviço
echo sudo cp mamute.service /etc/systemd/system/
echo sudo systemctl enable mamute
echo sudo systemctl start mamute
echo ```
echo.
echo ### 5. Configurar domínio ^(opcional^)
echo ```
echo 1. Comprar domínio ^(namecheap, godaddy^)
echo 2. Configurar DNS para IP da VM
echo 3. Configurar HTTPS com Let's Encrypt
echo 4. Nginx como reverse proxy
echo ```
echo.
echo ## 💰 Opção 2: VPS Comercial
echo.
echo ### Contabo ^(€4.99/mês^)
echo 1. Acesse: contabo.com
echo 2. VPS S: 4GB RAM, 50GB SSD
echo 3. Escolha Ubuntu 22.04
echo 4. Siga mesmos passos de instalação
echo.
echo ## 🎯 VANTAGENS CLOUD:
echo - ✅ Funciona 24h real
echo - ✅ Acesso de qualquer lugar
echo - ✅ IP fixo
echo - ✅ Não depende do seu notebook
echo - ✅ Backup automático
echo - ✅ Escalável
echo.
echo Criado em: %date% %time%
) > "GUIA_CLOUD_24H.md"

echo ✅ Guia criado: GUIA_CLOUD_24H.md
echo 📖 Abrir arquivo para ler? ^(s/n^)
set /p open="Resposta: "
if /i "%open%"=="s" start GUIA_CLOUD_24H.md
exit /b

:end
echo.
echo 💡 DICA: Para verificar se está funcionando 24h:
echo    1. Execute: python verificar_status_servidores.py  
echo    2. Feche o notebook
echo    3. Abra de outro dispositivo e acesse o IP
echo.
pause