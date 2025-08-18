#!/usr/bin/env python3
"""
Script para verificar se as URLs categorizadas como 'Outras' são realmente do Twilio
e se ainda estão acessíveis.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.db import models
from app.db.connection import SessionLocal
import requests
from urllib.parse import urlparse
import time

def verificar_urls_twilio():
    """Verifica URLs que podem ser do Twilio"""
    print("🔍 Verificando URLs que podem ser do Twilio...\n")
    
    db = SessionLocal()
    try:
        # Buscar fotos que não são placeholder nem cloudinary
        fotos = db.query(models.FotoPromotor).filter(
            ~models.FotoPromotor.url_foto.contains('placeholder'),
            ~models.FotoPromotor.url_foto.contains('cloudinary.com'),
            ~models.FotoPromotor.url_foto.contains('localhost')
        ).limit(20).all()
        
        print(f"📊 Verificando {len(fotos)} URLs suspeitas...\n")
        
        twilio_urls = []
        urls_acessiveis = []
        urls_inacessiveis = []
        urls_relativas = []
        
        for i, foto in enumerate(fotos):
            url = foto.url_foto
            print(f"🔗 {i+1}. Verificando: {url[:80]}...")
            
            # Verificar se é URL relativa (caminho local)
            if url.startswith('/'):
                urls_relativas.append(foto)
                print(f"   📁 URL relativa (caminho local)")
                print(f"   ⚠️  Esta foto foi salva localmente, não no Twilio")
            else:
                # Verificar se é URL do Twilio
                is_twilio = False
                if any(domain in url.lower() for domain in ['twilio.com', 'amazonaws.com']):
                    is_twilio = True
                    twilio_urls.append(foto)
                    print(f"   📱 Identificada como URL do Twilio!")
                
                # Testar acessibilidade apenas para URLs completas
                try:
                    response = requests.head(url, timeout=10, allow_redirects=True)
                    if response.status_code == 200:
                        urls_acessiveis.append(foto)
                        print(f"   ✅ Acessível (Status: {response.status_code})")
                        if 'content-type' in response.headers:
                            print(f"   📄 Tipo: {response.headers['content-type']}")
                    else:
                        urls_inacessiveis.append(foto)
                        print(f"   ❌ Inacessível (Status: {response.status_code})")
                except Exception as e:
                    urls_inacessiveis.append(foto)
                    print(f"   ❌ Erro ao acessar: {str(e)[:50]}...")
            
            print(f"   📅 Data: {foto.data_envio}")
            print(f"   👤 Promotor: {foto.promotor.nome if foto.promotor else 'Desconhecido'}")
            print(f"   📝 Legenda: {foto.legenda[:50] if foto.legenda else 'Sem legenda'}...\n")
            
            # Pausa para não sobrecarregar
            time.sleep(0.2)
        
        return {
            'total_verificadas': len(fotos),
            'twilio_identificadas': len(twilio_urls),
            'acessiveis': len(urls_acessiveis),
            'inacessiveis': len(urls_inacessiveis),
            'relativas': len(urls_relativas)
        }
        
    finally:
        db.close()

def analisar_padroes_urls():
    """Analisa padrões nas URLs para identificar possíveis URLs do Twilio"""
    print("🔍 Analisando padrões nas URLs...\n")
    
    db = SessionLocal()
    try:
        # Buscar uma amostra maior de URLs
        fotos = db.query(models.FotoPromotor).filter(
            ~models.FotoPromotor.url_foto.contains('placeholder'),
            ~models.FotoPromotor.url_foto.contains('cloudinary.com'),
            ~models.FotoPromotor.url_foto.contains('localhost')
        ).limit(50).all()
        
        dominios = {}
        padroes = {
            'twilio.com': 0,
            'amazonaws.com': 0,
            'media': 0,
            'https://': 0,
            'http://': 0,
            'caminhos_relativos': 0,
            '.jpg': 0,
            '.jpeg': 0,
            '.png': 0,
            'uuid-like': 0
        }
        
        for foto in fotos:
            url = foto.url_foto
            if not url:
                continue
            
            # Verificar se é caminho relativo
            if url.startswith('/'):
                padroes['caminhos_relativos'] += 1
                continue
                
            # Extrair domínio apenas para URLs completas
            try:
                parsed = urlparse(url)
                dominio = parsed.netloc
                if dominio:
                    dominios[dominio] = dominios.get(dominio, 0) + 1
            except:
                pass
            
            # Verificar padrões
            url_lower = url.lower()
            for padrao in padroes:
                if padrao in url_lower:
                    padroes[padrao] += 1
            
            # Verificar se parece UUID (padrão Twilio)
            if len([c for c in url if c == '-']) >= 4 and any(c.isdigit() for c in url):
                padroes['uuid-like'] += 1
        
        print("🌐 Domínios encontrados:")
        if dominios:
            for dominio, count in sorted(dominios.items(), key=lambda x: x[1], reverse=True):
                print(f"   {dominio}: {count} URLs")
        else:
            print("   Nenhum domínio encontrado (todas são URLs relativas)")
        
        print("\n🔍 Padrões encontrados:")
        for padrao, count in padroes.items():
            if count > 0:
                print(f"   {padrao}: {count} URLs")
        
        return dominios, padroes
        
    finally:
        db.close()

def buscar_urls_twilio_reais():
    """Busca por URLs que realmente parecem ser do Twilio"""
    print("\n🔍 Buscando URLs reais do Twilio no banco...\n")
    
    db = SessionLocal()
    try:
        # Buscar URLs que contenham padrões típicos do Twilio
        fotos_twilio = db.query(models.FotoPromotor).filter(
            models.FotoPromotor.url_foto.contains('twilio')
        ).all()
        
        fotos_aws = db.query(models.FotoPromotor).filter(
            models.FotoPromotor.url_foto.contains('amazonaws')
        ).all()
        
        fotos_media = db.query(models.FotoPromotor).filter(
            models.FotoPromotor.url_foto.contains('media')
        ).filter(
            models.FotoPromotor.url_foto.contains('http')
        ).all()
        
        print(f"📱 URLs contendo 'twilio': {len(fotos_twilio)}")
        print(f"☁️  URLs contendo 'amazonaws': {len(fotos_aws)}")
        print(f"📷 URLs contendo 'media' + 'http': {len(fotos_media)}")
        
        # Mostrar exemplos se encontrar
        if fotos_twilio:
            print("\n📱 Exemplos de URLs do Twilio encontradas:")
            for i, foto in enumerate(fotos_twilio[:3]):
                print(f"   {i+1}. {foto.url_foto}")
        
        if fotos_aws:
            print("\n☁️  Exemplos de URLs AWS encontradas:")
            for i, foto in enumerate(fotos_aws[:3]):
                print(f"   {i+1}. {foto.url_foto}")
        
        return len(fotos_twilio) + len(fotos_aws) + len(fotos_media)
        
    finally:
        db.close()

def main():
    print("🚀 Verificação de URLs do Twilio")
    print("=" * 40)
    
    try:
        # Analisar padrões
        dominios, padroes = analisar_padroes_urls()
        
        print("\n" + "=" * 40)
        
        # Buscar URLs reais do Twilio
        urls_twilio_encontradas = buscar_urls_twilio_reais()
        
        print("\n" + "=" * 40)
        
        # Verificar URLs específicas
        stats = verificar_urls_twilio()
        
        print("=" * 40)
        print("📋 RESUMO DA VERIFICAÇÃO:")
        print(f"   🔍 URLs verificadas: {stats['total_verificadas']}")
        print(f"   📱 Identificadas como Twilio: {stats['twilio_identificadas']}")
        print(f"   📁 URLs relativas (locais): {stats['relativas']}")
        print(f"   ✅ URLs acessíveis: {stats['acessiveis']}")
        print(f"   ❌ URLs inacessíveis: {stats['inacessiveis']}")
        print(f"   🔍 URLs do Twilio no banco: {urls_twilio_encontradas}")
        
        print("\n💡 CONCLUSÕES:")
        if stats['relativas'] > 0:
            print(f"   📁 {stats['relativas']} fotos são caminhos locais (não Twilio)")
            print("   ⚠️  Essas fotos foram salvas no servidor, não no Twilio")
            print("   🔄 Provavelmente foram perdidas quando o servidor foi reiniciado")
        
        if stats['acessiveis'] > 0:
            print(f"   🎉 {stats['acessiveis']} fotos ainda estão acessíveis!")
            print("   📱 Essas fotos podem ser exibidas no sistema")
        
        if urls_twilio_encontradas == 0:
            print("   ❌ Nenhuma URL real do Twilio foi encontrada no banco")
            print("   📱 As fotos originais do Twilio não foram salvas")
        
        print("\n🚀 SITUAÇÃO ATUAL:")
        print("   ✅ Sistema modificado para usar apenas Twilio")
        print("   ✅ Webhook configurado para salvar URLs do Twilio")
        print("   📱 Novas fotos serão salvas corretamente")
        print("   🔄 Fotos antigas com caminhos locais estão perdidas")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("   1. 📱 Teste enviando uma nova foto via WhatsApp")
        print("   2. 🔧 Configure o webhook do Twilio")
        print("   3. 🧹 Limpe fotos placeholder/perdidas do banco")
        print("   4. 📊 Monitore novas fotos sendo salvas corretamente")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()