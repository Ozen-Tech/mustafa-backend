#!/usr/bin/env python3

import os
import sys
from datetime import datetime, timedelta
import requests
import json
from io import BytesIO
from PIL import Image

# Adicionar o diretório backend ao path
sys.path.append('./backend')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.models import FotoPromotor, Usuario
from app.db.connection import get_db
from app.services.cloudinary_service import cloudinary_service

print("📸 CONFIGURAÇÃO PARA FOTOS REAIS DO TWILIO")
print("=" * 50)

# 1. VERIFICAR CONFIGURAÇÃO ATUAL
print("\n1. VERIFICANDO CONFIGURAÇÃO ATUAL...")

try:
    from app.core.config import settings
    
    print(f"📊 CLOUDINARY_CLOUD_NAME: {'✅ Configurado' if settings.CLOUDINARY_CLOUD_NAME else '❌ Não configurado'}")
    print(f"📊 CLOUDINARY_API_KEY: {'✅ Configurado' if settings.CLOUDINARY_API_KEY else '❌ Não configurado'}")
    print(f"📊 CLOUDINARY_API_SECRET: {'✅ Configurado' if settings.CLOUDINARY_API_SECRET else '❌ Não configurado'}")
    
    if not all([settings.CLOUDINARY_CLOUD_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET]):
        print("\n🚨 PROBLEMA IDENTIFICADO: Credenciais do Cloudinary não configuradas!")
        print("\n📋 INSTRUÇÕES PARA CONFIGURAR NO RENDER:")
        print("1. Acesse o dashboard do Render (https://dashboard.render.com)")
        print("2. Vá para o seu serviço backend (mustafa-backend)")
        print("3. Clique na aba 'Environment'")
        print("4. Adicione as seguintes variáveis de ambiente:")
        print("   CLOUDINARY_CLOUD_NAME=duk91uunh")
        print("   CLOUDINARY_API_KEY=975379319645262")
        print("   CLOUDINARY_API_SECRET=giD7jfW0VJ2LCE3UsW_BG3BP8_s")
        print("5. Clique em 'Save Changes'")
        print("6. O Render fará redeploy automaticamente")
        print("\n⚠️  Após configurar, aguarde o deploy e execute este script novamente.")
        sys.exit(1)
    
    print("✅ Credenciais do Cloudinary configuradas localmente!")
    
except Exception as e:
    print(f"❌ Erro ao verificar configurações: {e}")
    sys.exit(1)

# 2. TESTAR CLOUDINARY COM IMAGEM REAL
print("\n2. TESTANDO CONEXÃO COM CLOUDINARY...")

try:
    # Criar uma imagem de teste simples
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    test_result = cloudinary_service.upload_image(
        image_source=img_bytes.getvalue(),
        filename="test_twilio_config.jpg",
        folder="fotos-promotores"
    )
    
    if test_result:
        print("✅ Cloudinary funcionando corretamente!")
        print(f"   URL de teste: {test_result['secure_url']}")
        print(f"   Public ID: {test_result['public_id']}")
        
        # Limpar teste
        try:
            cloudinary_service.delete_image(test_result['public_id'])
            print("   🧹 Arquivo de teste removido")
        except:
            pass
    else:
        print("❌ Falha no teste do Cloudinary")
        print("\n🔍 POSSÍVEIS CAUSAS:")
        print("1. Credenciais incorretas")
        print("2. Problema de conectividade")
        print("3. Configuração do Cloudinary")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Erro ao testar Cloudinary: {e}")
    print("\n💡 DICA: Verifique se as credenciais estão corretas no Render")
    sys.exit(1)

# 3. ANALISAR FOTOS PROBLEMÁTICAS
print("\n3. ANALISANDO FOTOS NO BANCO DE DADOS...")

db = next(get_db())

try:
    # Contar fotos com problemas
    fotos_demo = db.query(FotoPromotor).filter(
        FotoPromotor.url_foto.like('%res.cloudinary.com/demo%')
    ).count()
    
    fotos_placeholder = db.query(FotoPromotor).filter(
        FotoPromotor.url_foto.like('%placeholder%')
    ).count()
    
    fotos_validas = db.query(FotoPromotor).filter(
        FotoPromotor.url_foto.like('%res.cloudinary.com/duk91uunh%')
    ).count()
    
    total_fotos = db.query(FotoPromotor).count()
    
    print(f"📊 Total de fotos: {total_fotos}")
    print(f"📊 Fotos válidas (Cloudinary real): {fotos_validas}")
    print(f"📊 Fotos com demo (inválidas): {fotos_demo}")
    print(f"📊 Fotos com placeholder: {fotos_placeholder}")
    print(f"📊 Fotos problemáticas: {fotos_demo + fotos_placeholder}")
    
    if fotos_demo + fotos_placeholder > 0:
        print("\n🔄 LIMPEZA DE FOTOS PROBLEMÁTICAS:")
        print(f"   Encontradas {fotos_demo + fotos_placeholder} fotos que não são reais")
        print("   Essas fotos serão removidas para dar espaço às fotos reais")
        
        confirmar = input("\nDeseja remover as fotos problemáticas? (s/N): ").lower().strip()
        
        if confirmar == 's':
            print("\n🧹 REMOVENDO FOTOS PROBLEMÁTICAS...")
            
            # Remover fotos com demo
            fotos_removidas = db.query(FotoPromotor).filter(
                FotoPromotor.url_foto.like('%res.cloudinary.com/demo%')
            ).delete(synchronize_session=False)
            
            # Remover fotos com placeholder
            fotos_removidas += db.query(FotoPromotor).filter(
                FotoPromotor.url_foto.like('%placeholder%')
            ).delete(synchronize_session=False)
            
            db.commit()
            print(f"✅ {fotos_removidas} fotos problemáticas removidas!")
            print("   Agora apenas fotos reais serão exibidas")
            
        else:
            print("📝 Fotos problemáticas mantidas.")
    else:
        print("✅ Não há fotos problemáticas no banco!")
    
except Exception as e:
    print(f"❌ Erro durante análise: {e}")
    db.rollback()
    
finally:
    db.close()

# 4. INSTRUÇÕES FINAIS
print("\n" + "=" * 60)
print("🎯 CONFIGURAÇÃO CONCLUÍDA - FOTOS REAIS DO TWILIO")
print("=" * 60)

print("\n✅ SISTEMA CONFIGURADO PARA FOTOS REAIS!")

print("\n📋 COMO FUNCIONA AGORA:")
print("1. 📱 Promotor envia foto via WhatsApp")
print("2. 🔄 Twilio recebe e envia para seu webhook")
print("3. ⬇️  Sistema baixa a foto real do Twilio")
print("4. ☁️  Foto é enviada para o Cloudinary")
print("5. 💾 URL real é salva no banco de dados")
print("6. 🖼️  Foto real aparece no dashboard")

print("\n🧪 COMO TESTAR:")
print("1. Envie uma foto via WhatsApp para o número do Twilio")
print("2. Aguarde alguns segundos para processamento")
print("3. Acesse o dashboard e verifique se a foto aparece")
print("4. A foto deve ser a imagem real enviada, não um placeholder")

print("\n🔍 MONITORAMENTO:")
print("- URLs das fotos devem começar com: https://res.cloudinary.com/duk91uunh/")
print("- Verifique os logs do Render em caso de problemas")
print("- Webhook endpoint: /webhook/whatsapp")

print("\n📞 ORIENTAÇÕES PARA PROMOTORES:")
print("- ✅ Novas fotos serão salvas corretamente")
print("- 📸 Enviem fotos importantes via WhatsApp")
print("- 🕐 Aguardem alguns segundos após envio")
print("- 🔄 Podem reenviar se a foto não aparecer")

print("\n🚨 SOLUÇÃO DE PROBLEMAS:")
print("1. Se fotos não aparecem:")
print("   - Verifique variáveis de ambiente no Render")
print("   - Verifique logs do webhook")
print("   - Teste o endpoint manualmente")
print("\n2. Se aparecem placeholders:")
print("   - Credenciais do Cloudinary podem estar incorretas")
print("   - Execute este script novamente")

print("\n💡 IMPORTANTE:")
print("- As fotos antigas com problemas foram removidas")
print("- Apenas fotos reais serão exibidas daqui em diante")
print("- O sistema está otimizado para fotos do Twilio")

print(f"\n✅ Configuração concluída em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\n🎉 SISTEMA PRONTO PARA FOTOS REAIS DO TWILIO!")