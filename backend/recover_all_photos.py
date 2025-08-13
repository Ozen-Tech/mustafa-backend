#!/usr/bin/env python3
"""
Script para recuperar TODAS as fotos existentes no banco de dados
e fazer upload para o Cloudinary, preservando o histórico completo.

Este script tenta múltiplas estratégias de recuperação:
1. Verificar se os arquivos ainda existem localmente
2. Tentar baixar das URLs antigas
3. Fazer upload para Cloudinary e atualizar o banco
"""

import os
import sys
import requests
from pathlib import Path
from typing import List, Tuple, Optional
import tempfile
from urllib.parse import urlparse

# Adicionar o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy.orm import Session
from db.connection import get_db
from db.models import FotoPromotor
from services.cloudinary_service import CloudinaryService

class PhotoRecoveryService:
    def __init__(self):
        self.cloudinary_service = CloudinaryService()
        self.recovered_count = 0
        self.failed_count = 0
        self.already_cloudinary_count = 0
        
    def is_cloudinary_url(self, url: str) -> bool:
        """Verifica se a URL já é do Cloudinary"""
        return 'cloudinary.com' in url or 'res.cloudinary.com' in url
    
    def is_local_url(self, url: str) -> bool:
        """Verifica se é uma URL local problemática"""
        return 'localhost' in url or '127.0.0.1' in url or url.startswith('/uploads')
    
    def extract_filename_from_url(self, url: str) -> Optional[str]:
        """Extrai o nome do arquivo da URL"""
        try:
            parsed = urlparse(url)
            return os.path.basename(parsed.path)
        except:
            return None
    
    def find_local_file(self, filename: str) -> Optional[str]:
        """Procura o arquivo em possíveis diretórios locais"""
        possible_paths = [
            f"uploads/fotos-promotores/{filename}",
            f"app/uploads/fotos-promotores/{filename}",
            f"/app/uploads/fotos-promotores/{filename}",
            f"../uploads/fotos-promotores/{filename}",
            f"./uploads/fotos-promotores/{filename}"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def download_from_url(self, url: str) -> Optional[bytes]:
        """Tenta baixar a imagem da URL antiga"""
        try:
            # Tentar diferentes variações da URL
            urls_to_try = [
                url,
                url.replace('localhost:8000', 'mustafa-backend.onrender.com'),
                url.replace('127.0.0.1:8000', 'mustafa-backend.onrender.com'),
            ]
            
            for try_url in urls_to_try:
                try:
                    response = requests.get(try_url, timeout=10)
                    if response.status_code == 200:
                        return response.content
                except:
                    continue
            return None
        except Exception as e:
            print(f"Erro ao baixar {url}: {e}")
            return None
    
    def recover_photo(self, foto: FotoPromotor, db: Session) -> bool:
        """Tenta recuperar uma foto específica"""
        print(f"\n📸 Processando foto ID {foto.id}: {foto.url_foto}")
        
        # Se já é do Cloudinary, pular
        if self.is_cloudinary_url(foto.url_foto):
            print("   ✅ Já está no Cloudinary")
            self.already_cloudinary_count += 1
            return True
        
        # Tentar encontrar arquivo local primeiro
        filename = self.extract_filename_from_url(foto.url_foto)
        if filename:
            local_path = self.find_local_file(filename)
            if local_path:
                print(f"   📁 Arquivo encontrado localmente: {local_path}")
                try:
                    result = self.cloudinary_service.upload_image(local_path)
                    if result:
                        # Atualizar no banco
                        foto.url_foto = result['secure_url']
                        foto.nome_arquivo_servidor = result['public_id']
                        db.commit()
                        print(f"   ✅ Recuperado do arquivo local!")
                        self.recovered_count += 1
                        return True
                except Exception as e:
                    print(f"   ❌ Erro no upload local: {e}")
        
        # Tentar baixar da URL antiga
        print("   🌐 Tentando baixar da URL antiga...")
        image_data = self.download_from_url(foto.url_foto)
        if image_data:
            try:
                # Salvar temporariamente
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                    temp_file.write(image_data)
                    temp_path = temp_file.name
                
                # Upload para Cloudinary
                result = self.cloudinary_service.upload_image(temp_path)
                if result:
                    # Atualizar no banco
                    foto.url_foto = result['secure_url']
                    foto.nome_arquivo_servidor = result['public_id']
                    db.commit()
                    print(f"   ✅ Recuperado via download!")
                    self.recovered_count += 1
                    
                    # Limpar arquivo temporário
                    os.unlink(temp_path)
                    return True
                
                # Limpar arquivo temporário em caso de erro
                os.unlink(temp_path)
            except Exception as e:
                print(f"   ❌ Erro no upload via download: {e}")
        
        print("   ❌ Não foi possível recuperar")
        self.failed_count += 1
        return False
    
    def recover_all_photos(self):
        """Recupera todas as fotos do banco de dados"""
        print("🚀 INICIANDO RECUPERAÇÃO COMPLETA DE FOTOS")
        print("=" * 50)
        
        db = next(get_db())
        try:
            # Buscar todas as fotos
            fotos = db.query(FotoPromotor).all()
            total_fotos = len(fotos)
            
            print(f"📊 Total de fotos encontradas: {total_fotos}")
            
            if total_fotos == 0:
                print("❌ Nenhuma foto encontrada no banco de dados")
                return
            
            # Processar cada foto
            for i, foto in enumerate(fotos, 1):
                print(f"\n[{i}/{total_fotos}] Processando...")
                self.recover_photo(foto, db)
            
            # Estatísticas finais
            print("\n" + "=" * 50)
            print("📊 RELATÓRIO FINAL DE RECUPERAÇÃO")
            print("=" * 50)
            print(f"✅ Fotos recuperadas: {self.recovered_count}")
            print(f"🔄 Já no Cloudinary: {self.already_cloudinary_count}")
            print(f"❌ Falhas na recuperação: {self.failed_count}")
            print(f"📊 Total processadas: {total_fotos}")
            
            success_rate = ((self.recovered_count + self.already_cloudinary_count) / total_fotos) * 100
            print(f"🎯 Taxa de sucesso: {success_rate:.1f}%")
            
            if self.recovered_count > 0:
                print(f"\n🎉 SUCESSO! {self.recovered_count} fotos foram recuperadas!")
            
            if self.failed_count > 0:
                print(f"\n⚠️  {self.failed_count} fotos não puderam ser recuperadas.")
                print("   Essas fotos podem ter sido perdidas permanentemente.")
                print("   Considere pedir aos promotores para reenviá-las.")
        
        finally:
            db.close()

def main():
    """Função principal"""
    try:
        recovery_service = PhotoRecoveryService()
        recovery_service.recover_all_photos()
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()