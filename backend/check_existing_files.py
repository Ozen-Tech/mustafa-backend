#!/usr/bin/env python3
"""
Script para verificar se os arquivos de foto ainda existem
no servidor atual antes de tentar a recuperação completa.
"""

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

# Adicionar o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy.orm import Session
from db.connection import get_db
from db.models import FotoPromotor

def extract_filename_from_url(url: str) -> str:
    """Extrai o nome do arquivo da URL"""
    try:
        parsed = urlparse(url)
        return os.path.basename(parsed.path)
    except:
        return ""

def find_local_file(filename: str) -> str:
    """Procura o arquivo em possíveis diretórios locais"""
    possible_paths = [
        f"uploads/fotos-promotores/{filename}",
        f"app/uploads/fotos-promotores/{filename}", 
        f"/app/uploads/fotos-promotores/{filename}",
        f"../uploads/fotos-promotores/{filename}",
        f"./uploads/fotos-promotores/{filename}",
        f"/opt/render/project/src/uploads/fotos-promotores/{filename}",
        f"/opt/render/project/uploads/fotos-promotores/{filename}"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return ""

def check_files():
    """Verifica quais arquivos ainda existem no servidor"""
    print("🔍 VERIFICANDO ARQUIVOS EXISTENTES NO SERVIDOR")
    print("=" * 50)
    
    db = next(get_db())
    try:
        # Buscar fotos com URLs locais
        fotos_locais = db.query(FotoPromotor).filter(
            FotoPromotor.url_foto.contains('localhost')
        ).all()
        
        print(f"📊 Fotos com URLs locais encontradas: {len(fotos_locais)}")
        
        if len(fotos_locais) == 0:
            print("✅ Nenhuma foto com URL local encontrada!")
            return
        
        arquivos_encontrados = 0
        arquivos_perdidos = 0
        
        print("\n🔍 Verificando existência dos arquivos...")
        
        for foto in fotos_locais:
            filename = extract_filename_from_url(foto.url_foto)
            if filename:
                local_path = find_local_file(filename)
                if local_path:
                    print(f"✅ ENCONTRADO: {filename} -> {local_path}")
                    arquivos_encontrados += 1
                else:
                    print(f"❌ PERDIDO: {filename}")
                    arquivos_perdidos += 1
            else:
                print(f"⚠️  URL inválida: {foto.url_foto}")
                arquivos_perdidos += 1
        
        print("\n" + "=" * 50)
        print("📊 RESULTADO DA VERIFICAÇÃO")
        print("=" * 50)
        print(f"✅ Arquivos encontrados: {arquivos_encontrados}")
        print(f"❌ Arquivos perdidos: {arquivos_perdidos}")
        print(f"📊 Total verificado: {len(fotos_locais)}")
        
        if arquivos_encontrados > 0:
            recovery_rate = (arquivos_encontrados / len(fotos_locais)) * 100
            print(f"🎯 Taxa de recuperação possível: {recovery_rate:.1f}%")
            print(f"\n🎉 BOM! {arquivos_encontrados} fotos podem ser recuperadas!")
            print("   Execute 'python manage.py recover-photos' para recuperá-las.")
        else:
            print("\n😞 Infelizmente, nenhum arquivo foi encontrado no servidor.")
            print("   As fotos podem ter sido perdidas no último deploy.")
        
        # Verificar diretórios existentes
        print("\n📁 Diretórios verificados:")
        possible_dirs = [
            "uploads/fotos-promotores/",
            "app/uploads/fotos-promotores/",
            "/app/uploads/fotos-promotores/",
            "../uploads/fotos-promotores/",
            "./uploads/fotos-promotores/",
            "/opt/render/project/src/uploads/fotos-promotores/",
            "/opt/render/project/uploads/fotos-promotores/"
        ]
        
        for dir_path in possible_dirs:
            if os.path.exists(dir_path):
                file_count = len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))])
                print(f"   ✅ {dir_path} - {file_count} arquivos")
            else:
                print(f"   ❌ {dir_path} - não existe")
    
    finally:
        db.close()

if __name__ == "__main__":
    check_files()