#!/usr/bin/env python3
"""
Script de Correção: URLs de Fotos Existentes

Este script corrige as URLs das fotos existentes no banco de dados,
removendo as referências locais e marcando-as como indisponíveis
ou tentando recuperá-las se ainda existirem.

Uso:
    python fix_existing_photos.py
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório do app ao path
sys.path.append(str(Path(__file__).parent / "app"))

from sqlalchemy.orm import Session
from app.db.connection import SessionLocal
from app.db.models import FotoPromotor

def fix_existing_photo_urls():
    """
    Corrige as URLs das fotos existentes no banco de dados.
    """
    db: Session = SessionLocal()
    
    try:
        print("🔍 Buscando fotos com URLs locais...")
        
        # Buscar todas as fotos que têm URLs locais
        fotos_locais = db.query(FotoPromotor).filter(
            FotoPromotor.url_foto.like('%localhost%')
        ).all()
        
        if not fotos_locais:
            print("✅ Nenhuma foto local encontrada!")
            return
        
        print(f"📸 Encontradas {len(fotos_locais)} fotos com URLs locais")
        
        opcao = input("\n🤔 O que deseja fazer?\n"
                     "1. Marcar como indisponíveis (URL placeholder)\n"
                     "2. Deletar registros das fotos locais\n"
                     "3. Cancelar\n"
                     "Escolha (1-3): ")
        
        if opcao == "1":
            # Opção 1: Marcar como indisponíveis
            placeholder_url = "https://via.placeholder.com/400x300/cccccc/666666?text=Foto+Indisponivel"
            
            for foto in fotos_locais:
                foto.url_foto = placeholder_url
                foto.nome_arquivo_servidor = f"placeholder_{foto.id}"
            
            db.commit()
            print(f"✅ {len(fotos_locais)} fotos marcadas como indisponíveis")
            print("💡 As fotos aparecerão com um placeholder até serem reenviadas")
            
        elif opcao == "2":
            # Opção 2: Deletar registros
            confirmacao = input(f"⚠️  Tem certeza que deseja DELETAR {len(fotos_locais)} registros de fotos? (sim/não): ")
            
            if confirmacao.lower() in ['sim', 's', 'yes', 'y']:
                for foto in fotos_locais:
                    db.delete(foto)
                
                db.commit()
                print(f"🗑️  {len(fotos_locais)} registros de fotos deletados")
                print("💡 Os promotores precisarão reenviar as fotos via WhatsApp")
            else:
                print("❌ Operação cancelada")
                
        else:
            print("❌ Operação cancelada")
            return
        
        print("\n🎉 Correção concluída!")
        
    except Exception as e:
        print(f"❌ Erro na correção: {str(e)}")
        db.rollback()
    
    finally:
        db.close()

def show_photo_stats():
    """
    Mostra estatísticas das fotos no banco.
    """
    db: Session = SessionLocal()
    
    try:
        total_fotos = db.query(FotoPromotor).count()
        fotos_locais = db.query(FotoPromotor).filter(
            FotoPromotor.url_foto.like('%localhost%')
        ).count()
        fotos_cloudinary = db.query(FotoPromotor).filter(
            FotoPromotor.url_foto.like('%cloudinary%')
        ).count()
        fotos_outras = total_fotos - fotos_locais - fotos_cloudinary
        
        print("📊 Estatísticas das Fotos:")
        print(f"   📸 Total de fotos: {total_fotos}")
        print(f"   🏠 URLs locais (problemáticas): {fotos_locais}")
        print(f"   ☁️  URLs Cloudinary (OK): {fotos_cloudinary}")
        print(f"   🔗 Outras URLs: {fotos_outras}")
        
        if fotos_locais > 0:
            print(f"\n⚠️  {fotos_locais} fotos precisam ser corrigidas")
        else:
            print("\n✅ Todas as fotos estão com URLs válidas!")
            
    except Exception as e:
        print(f"❌ Erro ao buscar estatísticas: {str(e)}")
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Correção de URLs de Fotos Existentes")
    print("=" * 40)
    
    # Mostrar estatísticas primeiro
    show_photo_stats()
    
    print("\n" + "=" * 40)
    
    # Executar correção se necessário
    fix_existing_photo_urls()
    
    print("\n" + "=" * 40)
    print("🏁 Processo finalizado!")