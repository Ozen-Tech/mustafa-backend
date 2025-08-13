#!/bin/sh

# Sair imediatamente se um comando falhar
set -e

# Executar o script de pre-inicialização do Python para criar as tabelas
echo "==> Executando prestart.py para garantir que as tabelas existem..."
python -m app.prestart
echo "==> prestart.py concluído."

# Executar o script para criar o superusuário (é seguro chamar sempre)
echo "==> Executando create_superuser.py..."
python -m app.create_superuser
echo "==> create_superuser.py concluído."

# Criar diretórios necessários para uploads
echo "==> Criando diretórios de upload..."
mkdir -p uploads/fotos_promotores
mkdir -p uploads
echo "==> Diretórios de upload criados."

# Iniciar o servidor Uvicorn como o processo principal
echo "==> Iniciando o servidor Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1