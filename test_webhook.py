#!/usr/bin/env python3

import requests
import json
from urllib.parse import urlencode

# URL do webhook em produção
WEBHOOK_URL = "https://mustafa-backend.onrender.com/webhook/whatsapp"

# Dados de teste simulando uma mensagem do Twilio
test_data = {
    'From': 'whatsapp:+5511999999999',  # Número de teste
    'MediaUrl0': 'https://api.twilio.com/2010-04-01/Accounts/test/Messages/test/Media/test',
    'NumMedia': '1',
    'Body': 'Teste de foto via WhatsApp'
}

print("🔍 Testando webhook do WhatsApp...")
print(f"URL: {WEBHOOK_URL}")
print(f"Dados de teste: {test_data}")
print("-" * 50)

try:
    # Testa se o webhook está acessível
    response = requests.post(
        WEBHOOK_URL,
        data=test_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        timeout=30
    )
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"✅ Response Headers: {dict(response.headers)}")
    print(f"✅ Response Content: {response.text}")
    
    if response.status_code == 200:
        print("\n🎉 WEBHOOK ESTÁ FUNCIONANDO!")
        print("O problema pode estar na configuração do Twilio ou nas credenciais.")
    else:
        print(f"\n❌ WEBHOOK RETORNOU ERRO: {response.status_code}")
        print("O webhook não está respondendo corretamente.")
        
except requests.exceptions.ConnectionError:
    print("❌ ERRO DE CONEXÃO: Não foi possível conectar ao webhook.")
    print("Verifique se o serviço está rodando em produção.")
except requests.exceptions.Timeout:
    print("❌ TIMEOUT: O webhook demorou muito para responder.")
except Exception as e:
    print(f"❌ ERRO INESPERADO: {e}")

print("\n" + "="*50)
print("PRÓXIMOS PASSOS PARA DIAGNÓSTICO:")
print("1. Verifique se o serviço está rodando no Render")
print("2. Verifique os logs do Render para erros")
print("3. Confirme a URL do webhook no painel do Twilio")
print("4. Teste enviando uma foto real via WhatsApp")
print("5. Verifique se as credenciais do Twilio estão corretas no Render")