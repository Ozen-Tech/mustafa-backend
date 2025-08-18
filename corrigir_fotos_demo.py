#!/usr/bin/env python3

import os
import sys
from datetime import datetime

# Adicionar o diretório backend ao path
sys.path.append('./backend')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.models import FotoPromotor, Usuario
from app.db.connection import get_db

print("🔧 CORREÇÃO RÁPIDA DE FOTOS COM URLs DE DEMO")
print("=" * 50)

# Conectar ao banco
db = next(get_db())

try:
    # 1. IDENTIFICAR FOTOS PROBLEMÁTICAS
    print("\n1. IDENTIFICANDO FOTOS PROBLEMÁTICAS...")
    
    # Contar fotos problemáticas
    fotos_demo = db.query(FotoPromotor).filter(
        FotoPromotor.url_foto.like('%res.cloudinary.com/demo%')
    ).count()
    
    fotos_sem_cloudinary = db.query(FotoPromotor).filter(
        ~FotoPromotor.url_foto.like('%res.cloudinary.com/duk91uunh%')
    ).count()
    
    print(f"📊 Fotos com URLs de demo: {fotos_demo}")
    print(f"📊 Fotos sem Cloudinary válido: {fotos_sem_cloudinary}")
    
    # 2. CORREÇÃO AUTOMÁTICA COM PLACEHOLDER
    print("\n🔄 CORRIGINDO AUTOMATICAMENTE COM PLACEHOLDER...")
    
    placeholder_url = "https://via.placeholder.com/400x300/e2e8f0/64748b?text=Foto+Indisponivel+Reenvie+via+WhatsApp"
    
    # Processar em lotes de 50 fotos
    lote_size = 50
    offset = 0
    total_corrigidas = 0
    
    while True:
        # Buscar próximo lote
        fotos_lote = db.query(FotoPromotor).filter(
            ~FotoPromotor.url_foto.like('%res.cloudinary.com/duk91uunh%')
        ).offset(offset).limit(lote_size).all()
        
        if not fotos_lote:
            break
        
        # Corrigir lote atual
        for foto in fotos_lote:
            try:
                foto.url_foto = placeholder_url
                foto.nome_arquivo_servidor = f"placeholder_{foto.id}_{foto.data_envio.strftime('%Y%m%d')}"
                total_corrigidas += 1
            except Exception as e:
                print(f"❌ Erro ao corrigir foto ID {foto.id}: {e}")
        
        # Commit do lote
        db.commit()
        print(f"   ✅ Lote processado: {len(fotos_lote)} fotos (Total: {total_corrigidas})")
        
        offset += lote_size
        
        # Limite de segurança
        if total_corrigidas >= 2000:
            print("   ⚠️  Limite de segurança atingido (2000 fotos)")
            break
    
    print(f"\n✅ {total_corrigidas} fotos corrigidas com placeholder!")
    
    # 3. ESTATÍSTICAS FINAIS
    print("\n" + "=" * 50)
    print("📊 ESTATÍSTICAS FINAIS")
    print("=" * 50)
    
    total_fotos = db.query(FotoPromotor).count()
    fotos_cloudinary_validas = db.query(FotoPromotor).filter(
        FotoPromotor.url_foto.like('%res.cloudinary.com/duk91uunh%')
    ).count()
    fotos_placeholder = db.query(FotoPromotor).filter(
        FotoPromotor.url_foto.like('%placeholder%')
    ).count()
    
    print(f"📊 Total de fotos: {total_fotos}")
    print(f"📊 Fotos com Cloudinary válido: {fotos_cloudinary_validas}")
    print(f"📊 Fotos com placeholder: {fotos_placeholder}")
    print(f"📊 Fotos problemáticas restantes: {total_fotos - fotos_cloudinary_validas - fotos_placeholder}")
    
    # 4. RECOMENDAÇÕES
    print("\n🎯 PRÓXIMOS PASSOS CRÍTICOS:")
    print("1. 🚨 CONFIGURAR CREDENCIAIS DO CLOUDINARY NO RENDER:")
    print("   CLOUDINARY_CLOUD_NAME=duk91uunh")
    print("   CLOUDINARY_API_KEY=975379319645262")
    print("   CLOUDINARY_API_SECRET=giD7jfW0VJ2LCE3UsW_BG3BP8_s")
    print("\n2. 🔄 FAZER REDEPLOY NO RENDER")
    print("\n3. 📱 TESTAR UPLOAD DE NOVA FOTO VIA WHATSAPP")
    print("\n4. 📢 ORIENTAR PROMOTORES A REENVIAREM FOTOS IMPORTANTES")
    
    print("\n💡 DICA: As fotos agora mostram placeholder informativo")
    print("   Os promotores podem reenviar as fotos via WhatsApp")
    
except Exception as e:
    print(f"❌ Erro durante a correção: {e}")
    db.rollback()
    
finally:
    db.close()
    print(f"\n✅ Processo concluído em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")