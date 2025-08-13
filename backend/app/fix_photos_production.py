#!/usr/bin/env python3
"""
Script de Produção: Correção Automática de URLs de Fotos

Este script pode ser executado no ambiente de produção (Render)
para corrigir automaticamente as URLs das fotos existentes.
"""

import os
from sqlalchemy.orm import Session
from db.connection import SessionLocal
from db.models import FotoPromotor

def fix_photos_in_production():
    """
    Corrige automaticamente as URLs das fotos em produção.
    """
    db: Session = SessionLocal()
    
    try:
        print("🔍 Verificando fotos com URLs problemáticas...")
        
        # Buscar fotos com URLs locais ou problemáticas
        fotos_problematicas = db.query(FotoPromotor).filter(
            FotoPromotor.url_foto.like('%localhost%')
        ).all()
        
        if not fotos_problematicas:
            print("✅ Nenhuma foto problemática encontrada!")
            return
        
        print(f"⚠️  Encontradas {len(fotos_problematicas)} fotos com URLs problemáticas")
        
        # URL de placeholder para fotos indisponíveis
        placeholder_url = "https://via.placeholder.com/400x300/e2e8f0/64748b?text=Foto+Temporariamente+Indisponivel"
        
        fotos_corrigidas = 0
        
        for foto in fotos_problematicas:
            try:
                # Atualizar para placeholder
                foto.url_foto = placeholder_url
                foto.nome_arquivo_servidor = f"placeholder_{foto.id}_{foto.data_envio.strftime('%Y%m%d')}"
                
                fotos_corrigidas += 1
                
            except Exception as e:
                print(f"❌ Erro ao corrigir foto ID {foto.id}: {str(e)}")
                continue
        
        # Salvar todas as alterações
        db.commit()
        
        print(f"✅ {fotos_corrigidas} fotos corrigidas com sucesso!")
        print("💡 As fotos agora mostram um placeholder até serem reenviadas")
        print("📱 Oriente os promotores a reenviarem fotos importantes via WhatsApp")
        
        return fotos_corrigidas
        
    except Exception as e:
        print(f"❌ Erro geral na correção: {str(e)}")
        db.rollback()
        return 0
    
    finally:
        db.close()

def get_photo_statistics():
    """
    Retorna estatísticas das fotos no banco.
    """
    db: Session = SessionLocal()
    
    try:
        total = db.query(FotoPromotor).count()
        problematicas = db.query(FotoPromotor).filter(
            FotoPromotor.url_foto.like('%localhost%')
        ).count()
        cloudinary = db.query(FotoPromotor).filter(
            FotoPromotor.url_foto.like('%cloudinary%')
        ).count()
        placeholders = db.query(FotoPromotor).filter(
            FotoPromotor.url_foto.like('%placeholder%')
        ).count()
        
        return {
            'total': total,
            'problematicas': problematicas,
            'cloudinary': cloudinary,
            'placeholders': placeholders
        }
        
    except Exception as e:
        print(f"❌ Erro ao buscar estatísticas: {str(e)}")
        return None
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Correção Automática de Fotos - Ambiente de Produção")
    print("=" * 55)
    
    # Mostrar estatísticas antes
    stats_antes = get_photo_statistics()
    if stats_antes:
        print(f"📊 Estatísticas ANTES da correção:")
        print(f"   📸 Total: {stats_antes['total']}")
        print(f"   ⚠️  Problemáticas: {stats_antes['problematicas']}")
        print(f"   ☁️  Cloudinary: {stats_antes['cloudinary']}")
        print(f"   🖼️  Placeholders: {stats_antes['placeholders']}")
    
    # Executar correção
    if stats_antes and stats_antes['problematicas'] > 0:
        print("\n🔧 Iniciando correção...")
        corrigidas = fix_photos_in_production()
        
        # Mostrar estatísticas depois
        stats_depois = get_photo_statistics()
        if stats_depois:
            print(f"\n📊 Estatísticas DEPOIS da correção:")
            print(f"   📸 Total: {stats_depois['total']}")
            print(f"   ⚠️  Problemáticas: {stats_depois['problematicas']}")
            print(f"   ☁️  Cloudinary: {stats_depois['cloudinary']}")
            print(f"   🖼️  Placeholders: {stats_depois['placeholders']}")
    else:
        print("\n✅ Nenhuma correção necessária!")
    
    print("\n" + "=" * 55)
    print("🏁 Processo concluído!")