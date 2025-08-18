#!/usr/bin/env python3

import requests
import json
from datetime import datetime

print("🔍 DIAGNÓSTICO DO PROBLEMA NO RENDER")
print("=" * 50)
print(f"Timestamp: {datetime.now()}")
print()

# 1. Testar se o serviço está online
print("1. TESTANDO SE O SERVIÇO ESTÁ ONLINE...")
try:
    response = requests.get("https://mustafa-backend.onrender.com/", timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Content: {response.text[:200]}...")
except Exception as e:
    print(f"   ❌ ERRO: {e}")

print()

# 2. Testar rotas específicas
print("2. TESTANDO ROTAS ESPECÍFICAS...")
routes_to_test = [
    "/docs",
    "/webhook/whatsapp",
    "/users/",
    "/fotos/"
]

for route in routes_to_test:
    try:
        url = f"https://mustafa-backend.onrender.com{route}"
        response = requests.get(url, timeout=10)
        print(f"   {route}: {response.status_code}")
    except Exception as e:
        print(f"   {route}: ❌ ERRO - {e}")

print()

# 3. Verificar se é problema de CORS
print("3. TESTANDO WEBHOOK COM POST...")
try:
    webhook_data = {
        'From': 'whatsapp:+5511999999999',
        'NumMedia': '0',
        'Body': 'teste'
    }
    response = requests.post(
        "https://mustafa-backend.onrender.com/webhook/whatsapp",
        data=webhook_data,
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    print(f"   Content: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ ERRO: {e}")

print()
print("=" * 50)
print("POSSÍVEIS CAUSAS DO PROBLEMA:")
print("1. ❌ Serviço não está rodando no Render")
print("2. ❌ Erro na inicialização da aplicação")
print("3. ❌ Problema com variáveis de ambiente")
print("4. ❌ Erro de dependências")
print("5. ❌ Problema de memória/recursos no Render")
print()
print("SOLUÇÕES RECOMENDADAS:")
print("1. 🔧 Verificar logs do Render")
print("2. 🔧 Fazer redeploy do serviço")
print("3. 🔧 Verificar se todas as variáveis de ambiente estão configuradas")
print("4. 🔧 Verificar se o requirements.txt está correto")
print("5. 🔧 Verificar se o comando de start está correto")