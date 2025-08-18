#!/usr/bin/env python3
"""
Script para verificar fotos existentes no banco de dados
e identificar quais podem ser recuperadas do Twilio.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db import models
from app.db.connection import SessionLocal
import requests
from urllib.parse import urlparse

def analisar_fotos_banco():
    """Analisa as fotos no banco de dados"""
    print("🔍 Analisando fotos no banco de dados...\n")
    
    db = SessionLocal()
    try:
        # Buscar todas as fotos
        fotos = db.query(models.FotoPromotor).all()
        
        print(f"📊 Total de fotos encontradas: {len(fotos)}\n")
        
        # Categorizar por tipo de URL
        cloudinary_urls = []
        twilio_urls = []
        localhost_urls = []
        placeholder_urls = []
        outras_urls = []
        
        for foto in fotos:
            url = foto.url_foto
            if not url:
                continue
                
            if 'cloudinary.com' in url:
                if 'demo/image/upload' in url or 'sample' in url:
                    placeholder_urls.append(foto)
                else:
                    cloudinary_urls.append(foto)
            elif 'twilio.com' in url or 'api.twilio.com' in url:
                twilio_urls.append(foto)
            elif 'localhost' in url or '127.0.0.1' in url:
                localhost_urls.append(foto)
            elif 'placeholder' in url.lower() or 'demo' in url.lower():
                placeholder_urls.append(foto)
            else:
                outras_urls.append(foto)
        
        print("📈 Distribuição por tipo de URL:")
        print(f"   🌩️  Cloudinary (real): {len(cloudinary_urls)} fotos")
        print(f"   🎭 Placeholder/Demo: {len(placeholder_urls)} fotos")
        print(f"   📱 Twilio: {len(twilio_urls)} fotos")
        print(f"   🏠 Localhost: {len(localhost_urls)} fotos")
        print(f"   ❓ Outras: {len(outras_urls)} fotos\n")
        
        # Mostrar exemplos de cada tipo
        if cloudinary_urls:
            print("🌩️ Exemplos de URLs do Cloudinary (reais):")
            for i, foto in enumerate(cloudinary_urls[:3]):
                print(f"   {i+1}. ID: {foto.id} | {foto.url_foto[:80]}...")
            print()
        
        if placeholder_urls:
            print("🎭 Exemplos de URLs Placeholder/Demo:")
            for i, foto in enumerate(placeholder_urls[:3]):
                print(f"   {i+1}. ID: {foto.id} | {foto.url_foto[:80]}...")
            print()
        
        if twilio_urls:
            print("📱 Exemplos de URLs do Twilio:")
            for i, foto in enumerate(twilio_urls[:3]):
                print(f"   {i+1}. ID: {foto.id} | {foto.url_foto[:80]}...")
            print()
        
        if outras_urls:
            print("❓ Exemplos de outras URLs:")
            for i, foto in enumerate(outras_urls[:3]):
                print(f"   {i+1}. ID: {foto.id} | {foto.url_foto[:80]}...")
            print()
        
        # Mostrar fotos mais recentes
        fotos_recentes = db.query(models.FotoPromotor).order_by(models.FotoPromotor.data_envio.desc()).limit(5).all()
        print("🕒 5 fotos mais recentes:")
        for i, foto in enumerate(fotos_recentes):
            promotor_nome = foto.promotor.nome if foto.promotor else "Desconhecido"
            url_tipo = "Cloudinary" if 'cloudinary.com' in (foto.url_foto or '') else "Twilio" if 'twilio.com' in (foto.url_foto or '') else "Outro"
            print(f"   {i+1}. {foto.data_envio} | {promotor_nome} | {url_tipo} | {foto.legenda[:30]}...")
        
        return {
            'total': len(fotos),
            'cloudinary': len(cloudinary_urls),
            'placeholder': len(placeholder_urls),
            'twilio': len(twilio_urls),
            'localhost': len(localhost_urls),
            'outras': len(outras_urls)
        }
        
    finally:
        db.close()

def verificar_promotores():
    """Verifica quantos promotores existem no sistema"""
    print("\n👥 Verificando promotores cadastrados...")
    
    db = SessionLocal()
    try:
        # Buscar usuários com perfil de promotor
        promotores = db.query(models.Usuario).filter(models.Usuario.perfil == 'promotor').all()
        print(f"📊 Total de promotores: {len(promotores)}")
        
        if promotores:
            print("\n📋 Alguns promotores cadastrados:")
            for i, promotor in enumerate(promotores[:5]):
                whatsapp = promotor.whatsapp_number or "Não informado"
                print(f"   {i+1}. {promotor.nome} | WhatsApp: {whatsapp}")
        
        # Verificar todos os perfis existentes
        perfis = db.query(models.Usuario.perfil).distinct().all()
        print(f"\n📋 Perfis encontrados no sistema: {[p[0] for p in perfis]}")
        
        return len(promotores)
        
    finally:
        db.close()

def verificar_urls_suspeitas(outras_urls_sample):
    """Verifica se as 'outras URLs' podem ser do Twilio"""
    print("\n🔍 Analisando URLs suspeitas...")
    
    db = SessionLocal()
    try:
        # Pegar uma amostra das 'outras' URLs
        outras_fotos = db.query(models.FotoPromotor).limit(10).all()
        
        print("🔗 Exemplos de URLs categorizadas como 'Outras':")
        for i, foto in enumerate(outras_fotos[:5]):
            url = foto.url_foto or "URL vazia"
            print(f"   {i+1}. {url}")
            
            # Verificar se pode ser Twilio
            if 'media' in url.lower() and ('twilio' in url.lower() or 'amazonaws' in url.lower()):
                print(f"      ⚠️  Esta URL pode ser do Twilio!")
        
    finally:
        db.close()

def main():
    print("🚀 Verificação do Sistema de Fotos (Pós-Cloudinary)")
    print("=" * 50)
    
    try:
        # Verificar conexão com banco
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Conexão com banco de dados OK\n")
        
        # Analisar fotos
        stats = analisar_fotos_banco()
        
        # Verificar promotores
        num_promotores = verificar_promotores()
        
        # Verificar URLs suspeitas
        verificar_urls_suspeitas(stats['outras'])
        
        print("\n" + "=" * 50)
        print("📋 RESUMO:")
        print(f"   📊 Total de fotos: {stats['total']}")
        print(f"   🌩️  Cloudinary (real): {stats['cloudinary']}")
        print(f"   🎭 Placeholder/Demo: {stats['placeholder']}")
        print(f"   📱 Twilio: {stats['twilio']}")
        print(f"   🏠 Localhost: {stats['localhost']} (perdidas)")
        print(f"   ❓ Outras: {stats['outras']} (podem ser Twilio!)")
        print(f"   👥 Promotores: {num_promotores}")
        
        print("\n💡 ANÁLISE:")
        if stats['outras'] > 0:
            print("   🔍 A maioria das URLs estão em 'Outras' - podem ser URLs do Twilio!")
            print("   📱 Essas fotos provavelmente ainda estão acessíveis no Twilio")
        if stats['twilio'] > 0:
            print("   ✅ Você já tem fotos do Twilio funcionando!")
        if stats['placeholder'] > 0:
            print("   🎭 Fotos placeholder podem ser removidas")
        if stats['localhost'] > 0:
            print("   ❌ Fotos localhost estão perdidas (URLs inválidas)")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("   1. 📱 Teste enviando uma nova foto via WhatsApp")
        print("   2. 🔧 Configure o webhook do Twilio para: https://seu-dominio.com/webhook/whatsapp")
        print("   3. 🔍 Verifique se as URLs em 'Outras' são realmente do Twilio")
        print("   4. 🧹 Considere limpar fotos placeholder/demo")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("🔍 Verifique se o banco de dados está acessível")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()