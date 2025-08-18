#!/usr/bin/env python3

import requests
import json
from datetime import datetime
import time

print("🔧 TESTE PÓS-CORREÇÃO DO RENDER")
print("=" * 50)
print(f"Timestamp: {datetime.now()}")
print()

def test_endpoint(url, method='GET', data=None, expected_status=200, description=""):
    """Testa um endpoint e retorna o resultado"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, data=data, timeout=10)
        
        success = response.status_code == expected_status
        status_icon = "✅" if success else "❌"
        
        print(f"{status_icon} {description}")
        print(f"   URL: {url}")
        print(f"   Status: {response.status_code} (esperado: {expected_status})")
        
        if not success:
            print(f"   Resposta: {response.text[:200]}...")
        
        return success
    except Exception as e:
        print(f"❌ {description}")
        print(f"   ERRO: {e}")
        return False

print("1. TESTANDO SAÚDE DA API...")
api_health = test_endpoint(
    "https://mustafa-backend-6ywg.onrender.com/",
    description="API Principal"
)

print("\n2. TESTANDO DOCUMENTAÇÃO...")
docs_health = test_endpoint(
    "https://mustafa-backend-6ywg.onrender.com/docs",
    description="Documentação Swagger"
)

print("\n3. TESTANDO WEBHOOK DO WHATSAPP...")
webhook_data = {
    'From': 'whatsapp:+5511999999999',
    'NumMedia': '0',
    'Body': 'teste automatizado'
}
webhook_health = test_endpoint(
    "https://mustafa-backend-6ywg.onrender.com/webhook/whatsapp",
    method='POST',
    data=webhook_data,
    description="Webhook WhatsApp"
)

print("\n4. TESTANDO ROTA DE USUÁRIOS...")
users_health = test_endpoint(
    "https://mustafa-backend-6ywg.onrender.com/users/",
    expected_status=422,  # Esperamos 422 porque não enviamos dados
    description="Rota de Usuários"
)

print("\n5. TESTANDO ROTA DE FOTOS...")
fotos_health = test_endpoint(
    "https://mustafa-backend-6ywg.onrender.com/fotos/",
    expected_status=401,  # Esperamos 401 porque não temos token
    description="Rota de Fotos"
)

print("\n" + "=" * 50)
print("📊 RESUMO DOS TESTES")
print("=" * 50)

tests = [
    ("API Principal", api_health),
    ("Documentação", docs_health),
    ("Webhook WhatsApp", webhook_health),
    ("Rota Usuários", users_health),
    ("Rota Fotos", fotos_health)
]

passed = sum(1 for _, result in tests if result)
total = len(tests)

for name, result in tests:
    status = "✅ PASSOU" if result else "❌ FALHOU"
    print(f"{status} - {name}")

print(f"\n📈 RESULTADO: {passed}/{total} testes passaram")

if passed == total:
    print("\n🎉 PARABÉNS! O RENDER ESTÁ FUNCIONANDO PERFEITAMENTE!")
    print("\n📱 PRÓXIMOS PASSOS:")
    print("1. Teste enviando uma foto real via WhatsApp")
    print("2. Verifique se a foto aparece no sistema")
    print("3. Confirme se está sendo salva no Cloudinary")
elif passed >= 3:
    print("\n⚠️ RENDER ESTÁ FUNCIONANDO, MAS COM ALGUNS PROBLEMAS")
    print("\n🔧 AÇÕES RECOMENDADAS:")
    print("1. Verifique os logs do Render para erros específicos")
    print("2. Confirme se todas as variáveis de ambiente estão configuradas")
    print("3. Teste o webhook do WhatsApp manualmente")
else:
    print("\n🚨 RENDER AINDA NÃO ESTÁ FUNCIONANDO CORRETAMENTE")
    print("\n🛠️ AÇÕES URGENTES:")
    print("1. Verifique se o redeploy foi concluído")
    print("2. Confirme todas as variáveis de ambiente")
    print("3. Verifique os logs do Render para erros")
    print("4. Se necessário, entre em contato com o suporte do Render")

print("\n" + "=" * 50)
print("Para mais detalhes, consulte: SOLUCAO_RENDER_URGENTE.md")