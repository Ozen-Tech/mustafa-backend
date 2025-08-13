#!/usr/bin/env python3
"""
Script de Migração: Fotos Locais → Cloudinary

Este script migra as fotos existentes no banco de dados que possuem URLs locais
para o Cloudinary, atualizando as URLs no banco de dados.

Uso:
    python migrate_photos_to_cloudinary.py
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório do app ao path para importar os módulos
sys.path.append(str(Path(__file__).parent / "app"))

from sqlalchemy.orm import Session
from app.db.connection import SessionLocal
from app.db.models import FotoPromotor
from app.services.cloudinary_service import cloudinary_service

def migrate_photos_to_cloudinary():
    """
    Migra fotos locais para o Cloudinary e atualiza as URLs no banco.
    """
    db: Session = SessionLocal()
    
    try:
        print("🔍 Buscando fotos com URLs locais...")
        
        # Buscar fotos que têm URLs locais (contêm localhost ou são caminhos relativos)
        fotos_locais = db.query(FotoPromotor).filter(
            FotoPromotor.url_foto.like('%localhost%')
        ).all()
        
        if not fotos_locais:
            print("✅ Nenhuma foto local encontrada. Todas as fotos já estão no Cloudinary!")
            return
        
        print(f"📸 Encontradas {len(fotos_locais)} fotos para migrar")
        
        migradas = 0
        erros = 0
        
        for foto in fotos_locais:
            try:
                print(f"\n📤 Migrando foto ID {foto.id}...")
                print(f"   URL atual: {foto.url_foto}")
                print(f"   Arquivo: {foto.nome_arquivo_servidor}")
                
                # Construir o caminho do arquivo local
                upload_dir = Path("uploads/fotos_promotores")
                arquivo_local = upload_dir / foto.nome_arquivo_servidor
                
                # Verificar se o arquivo existe
                if not arquivo_local.exists():
                    print(f"   ⚠️  Arquivo não encontrado: {arquivo_local}")
                    print(f"   ❌ Pulando foto ID {foto.id}")
                    erros += 1
                    continue
                
                # Fazer upload para o Cloudinary
                print(f"   ☁️  Fazendo upload para Cloudinary...")
                cloudinary_url, public_id = cloudinary_service.upload_image(
                    str(arquivo_local),
                    folder="fotos_promotores"
                )
                
                # Atualizar no banco de dados
                foto.url_foto = cloudinary_url
                foto.nome_arquivo_servidor = public_id  # Agora armazena o public_id
                
                db.commit()
                
                print(f"   ✅ Migrada com sucesso!")
                print(f"   Nova URL: {cloudinary_url}")
                print(f"   Public ID: {public_id}")
                
                migradas += 1
                
            except Exception as e:
                print(f"   ❌ Erro ao migrar foto ID {foto.id}: {str(e)}")
                erros += 1
                db.rollback()
                continue
        
        print(f"\n📊 Resumo da Migração:")
        print(f"   ✅ Fotos migradas: {migradas}")
        print(f"   ❌ Erros: {erros}")
        print(f"   📸 Total processadas: {len(fotos_locais)}")
        
        if migradas > 0:
            print(f"\n🎉 Migração concluída! {migradas} fotos agora estão no Cloudinary.")
        
    except Exception as e:
        print(f"❌ Erro geral na migração: {str(e)}")
        db.rollback()
    
    finally:
        db.close()

def check_cloudinary_config():
    """
    Verifica se as configurações do Cloudinary estão definidas.
    """
    required_vars = ['CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Configurações do Cloudinary não encontradas:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Configure as variáveis de ambiente antes de executar a migração.")
        return False
    
    print("✅ Configurações do Cloudinary encontradas!")
    return True

if __name__ == "__main__":
    print("🚀 Iniciando Migração de Fotos para Cloudinary")
    print("=" * 50)
    
    # Verificar configurações
    if not check_cloudinary_config():
        sys.exit(1)
    
    # Executar migração
    migrate_photos_to_cloudinary()
    
    print("\n" + "=" * 50)
    print("🏁 Migração finalizada!")