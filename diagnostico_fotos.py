#!/usr/bin/env python3

import os
import sys
import requests
from datetime import datetime

# Adicionar o diretório backend ao path
sys.path.append('./backend')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.models import FotoPromotor, Usuario
from app.db.connection import get_db

print("🔍 DIAGNÓSTICO COMPLETO DO SISTEMA DE FOTOS")
print("=" * 50)

# 1. VERIFICAR CONEXÃO COM O BANCO DE DADOS
print("\n1. TESTANDO CONEXÃO COM BANCO DE DADOS...")
try:
    db = next(get_db())
    result = db.execute(text("SELECT 1"))
    print("✅ Conexão com banco de dados: OK")
except Exception as e:
    print(f"❌ Erro na conexão com banco: {e}")
    sys.exit(1)

# 2. VERIFICAR FOTOS NO BANCO
print("\n2. ANALISANDO FOTOS NO BANCO DE DADOS...")
try:
    total_fotos = db.query(FotoPromotor).count()
    fotos_com_url = db.query(FotoPromotor).filter(FotoPromotor.url_foto.isnot(None)).count()
    fotos_cloudinary = db.query(FotoPromotor).filter(FotoPromotor.url_foto.like('%cloudinary%')).count()
    fotos_localhost = db.query(FotoPromotor).filter(FotoPromotor.url_foto.like('%localhost%')).count()
    fotos_render = db.query(FotoPromotor).filter(FotoPromotor.url_foto.like('%render%')).count()
    fotos_placeholder = db.query(FotoPromotor).filter(FotoPromotor.url_foto.like('%placeholder%')).count()
    
    print(f"📊 Total de fotos: {total_fotos}")
    print(f"📊 Fotos com URL: {fotos_com_url}")
    print(f"📊 Fotos no Cloudinary: {fotos_cloudinary}")
    print(f"📊 Fotos localhost: {fotos_localhost}")
    print(f"📊 Fotos render: {fotos_render}")
    print(f"📊 Fotos placeholder: {fotos_placeholder}")
    
    # Mostrar algumas URLs de exemplo
    print("\n📋 EXEMPLOS DE URLs NO BANCO:")
    fotos_exemplo = db.query(FotoPromotor).limit(5).all()
    for foto in fotos_exemplo:
        print(f"  ID {foto.id}: {foto.url_foto[:80]}...")
        
except Exception as e:
    print(f"❌ Erro ao analisar fotos: {e}")

# 3. TESTAR API DO BACKEND
print("\n3. TESTANDO API DO BACKEND...")
backend_urls = [
    "https://mustafa-backend.onrender.com",
    "https://mustafa-backend-6ywg.onrender.com"
]

api_funcionando = False
for url in backend_urls:
    try:
        response = requests.get(f"{url}/", timeout=10)
        if response.status_code == 200:
            print(f"✅ API funcionando: {url}")
            api_funcionando = True
            backend_url = url
            break
    except Exception as e:
        print(f"❌ API não responde: {url} - {e}")

if not api_funcionando:
    print("🚨 NENHUMA API DO BACKEND ESTÁ FUNCIONANDO!")
    print("   Isso explica por que as fotos não aparecem.")
else:
    # 4. TESTAR ENDPOINT DE FOTOS
    print("\n4. TESTANDO ENDPOINT DE FOTOS...")
    try:
        # Tentar sem autenticação primeiro
        response = requests.get(f"{backend_url}/fotos", timeout=10)
        print(f"📡 Status do endpoint /fotos: {response.status_code}")
        
        if response.status_code == 401:
            print("🔐 Endpoint requer autenticação (normal)")
        elif response.status_code == 200:
            data = response.json()
            print(f"📊 Fotos retornadas pela API: {len(data)}")
            if data:
                print(f"📋 Exemplo de foto da API: {data[0]}")
    except Exception as e:
        print(f"❌ Erro ao testar endpoint de fotos: {e}")

# 5. VERIFICAR CREDENCIAIS CLOUDINARY
print("\n5. VERIFICANDO CREDENCIAIS CLOUDINARY...")
cloudinary_vars = ['CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']
cloudinary_ok = True

for var in cloudinary_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: {value[:10]}...")
    else:
        print(f"❌ {var}: NÃO CONFIGURADA")
        cloudinary_ok = False

if cloudinary_ok:
    print("✅ Credenciais Cloudinary parecem estar configuradas")
else:
    print("❌ Credenciais Cloudinary incompletas")

# 6. VERIFICAR WEBHOOK DO TWILIO
print("\n6. TESTANDO WEBHOOK DO TWILIO...")
if api_funcionando:
    try:
        webhook_data = {
            'From': 'whatsapp:+5511999999999',
            'NumMedia': '0',
            'Body': 'teste diagnostico'
        }
        response = requests.post(f"{backend_url}/webhook/whatsapp", data=webhook_data, timeout=10)
        print(f"📡 Status do webhook: {response.status_code}")
        if response.status_code == 200:
            print("✅ Webhook do Twilio funcionando")
        else:
            print(f"❌ Webhook retornou erro: {response.text}")
    except Exception as e:
        print(f"❌ Erro ao testar webhook: {e}")

# 7. RESUMO E RECOMENDAÇÕES
print("\n" + "=" * 50)
print("📋 RESUMO DO DIAGNÓSTICO")
print("=" * 50)

problemas = []
solucoes = []

if not api_funcionando:
    problemas.append("🚨 API do backend não está funcionando")
    solucoes.append("1. Verificar se o serviço está rodando no Render")
    solucoes.append("2. Verificar logs do Render para erros")
    solucoes.append("3. Fazer redeploy se necessário")

if fotos_localhost > 0:
    problemas.append(f"⚠️  {fotos_localhost} fotos com URLs localhost (não funcionam em produção)")
    solucoes.append("4. Executar script de correção de fotos")

if fotos_cloudinary == 0 and total_fotos > 0:
    problemas.append("⚠️  Nenhuma foto está usando Cloudinary")
    solucoes.append("5. Verificar se o upload para Cloudinary está funcionando")

if not cloudinary_ok:
    problemas.append("⚠️  Credenciais do Cloudinary incompletas")
    solucoes.append("6. Configurar variáveis de ambiente do Cloudinary")

if problemas:
    print("\n🚨 PROBLEMAS IDENTIFICADOS:")
    for problema in problemas:
        print(f"   {problema}")
    
    print("\n🛠️  SOLUÇÕES RECOMENDADAS:")
    for solucao in solucoes:
        print(f"   {solucao}")
else:
    print("\n🎉 NENHUM PROBLEMA CRÍTICO IDENTIFICADO!")
    print("   O sistema parece estar funcionando corretamente.")

print("\n" + "=" * 50)
print(f"Diagnóstico concluído em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 50)

db.close()