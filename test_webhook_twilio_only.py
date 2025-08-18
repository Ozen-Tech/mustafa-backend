#!/usr/bin/env python3
"""
Script para testar o webhook do WhatsApp após remoção do Cloudinary.
Testa se o sistema consegue processar fotos usando apenas URLs do Twilio.
"""

import requests
import json
from urllib.parse import urlencode

# URL do webhook local
WEBHOOK_URL = "http://localhost:8000/webhook/whatsapp"

# Dados de teste simulando uma mensagem do Twilio com foto
test_data = {
    "From": "whatsapp:+5511999999999",  # Número de teste
    "MediaUrl0": "https://api.twilio.com/2010-04-01/Accounts/test/Messages/test/Media/test.jpg",  # URL de teste
    "NumMedia": "1",
    "Body": "Foto de teste do promotor"
}

def test_webhook():
    """Testa o webhook do WhatsApp"""
    print("🧪 Testando webhook do WhatsApp (apenas Twilio)...")
    print(f"📡 URL: {WEBHOOK_URL}")
    print(f"📋 Dados: {test_data}")
    
    try:
        # Enviar requisição POST com dados form-encoded
        response = requests.post(
            WEBHOOK_URL,
            data=test_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        print(f"\n✅ Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        print(f"🔧 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\n🎉 Webhook respondeu corretamente!")
            print("📝 A foto deve ser processada em background.")
            print("💡 Verifique os logs do servidor para confirmar o processamento.")
        else:
            print(f"\n❌ Erro: Status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n💥 Erro na requisição: {e}")
        print("🔍 Verifique se o servidor está rodando em http://localhost:8000")

def test_webhook_without_media():
    """Testa webhook sem mídia (apenas texto)"""
    print("\n🧪 Testando webhook sem mídia...")
    
    text_data = {
        "From": "whatsapp:+5511999999999",
        "NumMedia": "0",
        "Body": "Mensagem de texto sem foto"
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            data=text_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("🎉 Webhook para mensagem de texto funcionou!")
        
    except requests.exceptions.RequestException as e:
        print(f"💥 Erro: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes do webhook modificado...")
    print("📌 Este teste verifica se o sistema funciona sem Cloudinary")
    print("📌 As fotos agora são salvas com URLs diretas do Twilio\n")
    
    test_webhook()
    test_webhook_without_media()
    
    print("\n✨ Testes concluídos!")
    print("📊 Para verificar se funcionou:")
    print("   1. Verifique os logs do servidor")
    print("   2. Consulte o banco de dados para ver se a foto foi salva")
    print("   3. Teste com um número real de promotor cadastrado")