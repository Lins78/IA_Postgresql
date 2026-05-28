@echo off
echo Criando repositorio IA_Postgresql no GitHub...
echo.
echo 1. Navegando para o diretorio do projeto
cd /d "C:\Users\carlo\Desktop\Projetos\IA_Postgresql"

echo 2. Verificando status do git
git status

echo 3. Criando repositorio no GitHub usando GitHub CLI
gh repo create IA_Postgresql --public --description "Sistema IA com PostgreSQL - Projeto Mamute completo" --source=. --push

echo 4. Verificando se o push foi bem-sucedido
git remote -v

echo.
echo Repositorio criado com sucesso!
echo Acesse: https://github.com/Lins78/IA_Postgresql
pause