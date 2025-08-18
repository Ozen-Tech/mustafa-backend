#!/usr/bin/env python3
"""
Script para recuperar fotos do dashboard do Twilio e atualizar o banco de dados.

Este script:
1. Conecta à API do Twilio
2. Lista todas as mensagens com mídia dos últimos meses
3. Baixa as fotos que ainda estão disponíveis
4. Salva as fotos localmente ou em um serviço de armazenamento
5. Atualiza as URLs no banco de dados

Uso:
    python scripts/recover_twilio_photos.py [--dry-run] [--limit N]
"""

import os
import sys
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import mimetypes
from typing import List, Dict, Optional

# Carregar variáveis de ambiente ANTES de importar settings
from dotenv import load_dotenv
load_dotenv()

# Adicionar o diretório raiz ao path para importar módulos da aplicação
sys.path.append(str(Path(__file__).parent.parent))

from twilio.rest import Client
from app.db.connection import SessionLocal
from app.db.models import FotoPromotor
from app.core.config import settings
from sqlalchemy import text

class TwilioPhotoRecovery:
    def __init__(self, dry_run: bool = False, limit: Optional[int] = None):
        self.dry_run = dry_run
        self.limit = limit
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.db = SessionLocal()
        
        # Diretório para salvar as fotos recuperadas
        self.photos_dir = Path("recovered_photos")
        self.photos_dir.mkdir(exist_ok=True)
        
        # Estatísticas
        self.stats = {
            'messages_processed': 0,
            'media_found': 0,
            'photos_downloaded': 0,
            'database_updated': 0,
            'errors': 0
        }
    
    def get_file_extension(self, content_type: str) -> str:
        """Determina a extensão do arquivo baseada no content-type."""
        ext = mimetypes.guess_extension(content_type)
        if ext:
            return ext
        
        # Fallbacks para tipos comuns
        if 'jpeg' in content_type or 'jpg' in content_type:
            return '.jpg'
        elif 'png' in content_type:
            return '.png'
        elif 'gif' in content_type:
            return '.gif'
        elif 'webp' in content_type:
            return '.webp'
        else:
            return '.jpg'  # Default
    
    def generate_filename(self, media_sid: str, content_type: str) -> str:
        """Gera um nome de arquivo único baseado no media SID."""
        ext = self.get_file_extension(content_type)
        return f"{media_sid}{ext}"
    
    def download_media(self, media_url: str, filename: str) -> bool:
        """Baixa um arquivo de mídia do Twilio."""
        try:
            response = requests.get(
                media_url,
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                timeout=30
            )
            
            if response.status_code == 200:
                file_path = self.photos_dir / filename
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"Erro ao baixar {media_url}: Status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Erro ao baixar {media_url}: {str(e)}")
            self.stats['errors'] += 1
            return False
    
    def update_database_url(self, old_url: str, new_url: str) -> bool:
        """Atualiza a URL no banco de dados."""
        try:
            if self.dry_run:
                print(f"[DRY RUN] Atualizaria URL: {old_url} -> {new_url}")
                return True
            
            result = self.db.execute(
                text("UPDATE fotos_promotores SET url_foto = :new_url WHERE url_foto = :old_url"),
                {"new_url": new_url, "old_url": old_url}
            )
            self.db.commit()
            
            if result.rowcount > 0:
                self.stats['database_updated'] += result.rowcount
                return True
            return False
            
        except Exception as e:
            print(f"Erro ao atualizar banco de dados: {str(e)}")
            self.db.rollback()
            self.stats['errors'] += 1
            return False
    
    def create_new_photo_record(self, media_sid: str, new_url: str, message) -> bool:
        """Cria um novo registro de foto no banco de dados."""
        try:
            if self.dry_run:
                print(f"[DRY RUN] Criaria novo registro: {media_sid} -> {new_url}")
                return True
            
            # Extrair número do telefone da mensagem
            phone_number = message.from_
            if phone_number.startswith('+'):
                phone_number = phone_number[1:]
            
            # Buscar ou criar usuário promotor baseado no telefone
            promotor = self.db.execute(
                text("SELECT id, empresa_id FROM usuarios WHERE whatsapp_number = :phone"),
                {"phone": phone_number}
            ).fetchone()
            
            if not promotor:
                # Se não encontrar o promotor, usar um padrão ou pular
                print(f"Promotor não encontrado para telefone {phone_number}, pulando...")
                return False
            
            # Gerar nome único para o arquivo
            filename = f"recovered_{media_sid}.jpg"
            
            # Inserir novo registro
            result = self.db.execute(
                text("""
                    INSERT INTO fotos_promotores (url_foto, nome_arquivo_servidor, data_envio, promotor_id, empresa_id, legenda)
                    VALUES (:url_foto, :nome_arquivo, :data_envio, :promotor_id, :empresa_id, :legenda)
                """),
                {
                    "url_foto": new_url,
                    "nome_arquivo": filename,
                    "data_envio": message.date_sent,
                    "promotor_id": promotor[0],
                    "empresa_id": promotor[1],
                    "legenda": f"Foto recuperada do Twilio - Media SID: {media_sid}"
                }
            )
            self.db.commit()
            
            if result.rowcount > 0:
                self.stats['database_updated'] += result.rowcount
                return True
            return False
            
        except Exception as e:
            print(f"Erro ao criar novo registro: {str(e)}")
            self.db.rollback()
            self.stats['errors'] += 1
            return False
    
    def get_existing_twilio_urls(self) -> List[str]:
        """Recupera todas as URLs do Twilio existentes no banco de dados."""
        try:
            result = self.db.execute(
                text("SELECT DISTINCT url_foto FROM fotos_promotores WHERE url_foto LIKE '%api.twilio.com%'")
            ).fetchall()
            return [row[0] for row in result]
        except Exception as e:
            print(f"Erro ao buscar URLs existentes: {str(e)}")
            return []
    
    def process_messages(self, days_back: int = 90):
        """Processa mensagens do Twilio dos últimos N dias."""
        print(f"Buscando mensagens dos últimos {days_back} dias...")
        
        # Data de início
        date_sent_after = datetime.now() - timedelta(days=days_back)
        
        try:
            # Buscar mensagens com mídia
            messages = self.client.messages.list(
                date_sent_after=date_sent_after,
                limit=self.limit
            )
            
            print(f"Encontradas {len(messages)} mensagens para processar")
            
            for message in messages:
                self.stats['messages_processed'] += 1
                
                if self.stats['messages_processed'] % 100 == 0:
                    print(f"Processadas {self.stats['messages_processed']} mensagens...")
                
                # Buscar mídia da mensagem
                media_list = self.client.messages(message.sid).media.list()
                
                for media in media_list:
                    self.stats['media_found'] += 1
                    
                    # Verificar se é uma imagem
                    if media.content_type and media.content_type.startswith('image/'):
                        self.process_media(message, media)
                        
        except Exception as e:
            print(f"Erro ao processar mensagens: {str(e)}")
            self.stats['errors'] += 1
    
    def process_media(self, message, media):
        """Processa um item de mídia específico."""
        try:
            # Gerar nome do arquivo
            filename = self.generate_filename(media.sid, media.content_type)
            
            # URL original do Twilio
            original_url = f"https://api.twilio.com{media.uri.replace('.json', '')}"
            
            print(f"Processando mídia: {media.sid} ({media.content_type})")
            
            # Baixar a mídia
            if self.download_media(original_url, filename):
                self.stats['photos_downloaded'] += 1
                
                # Nova URL (pode ser local ou de um serviço de armazenamento)
                # Por enquanto, vamos usar uma URL local
                new_url = f"/recovered_photos/{filename}"
                
                # Verificar se já existe um registro com esta URL ou legenda contendo o media_sid
                existing_record = self.db.execute(
                    text("SELECT id FROM fotos_promotores WHERE legenda LIKE :media_sid_pattern OR url_foto = :new_url"),
                    {"media_sid_pattern": f"%{media.sid}%", "new_url": new_url}
                ).fetchone()
                
                if existing_record:
                    # Atualizar registro existente
                    self.db.execute(
                        text("UPDATE fotos_promotores SET url_foto = :new_url WHERE id = :id"),
                        {"new_url": new_url, "id": existing_record[0]}
                    )
                    self.db.commit()
                    self.stats['database_updated'] += 1
                    print(f"Registro existente atualizado: {media.sid} -> {new_url}")
                else:
                    # Tentar atualizar URLs antigas do Twilio
                    existing_urls = self.get_existing_twilio_urls()
                    matching_urls = [url for url in existing_urls if media.sid in url]
                    
                    if matching_urls:
                        for old_url in matching_urls:
                            self.update_database_url(old_url, new_url)
                            print(f"URL atualizada: {old_url} -> {new_url}")
                    else:
                        # Criar novo registro
                        if self.create_new_photo_record(media.sid, new_url, message):
                            print(f"Novo registro criado: {media.sid} -> {new_url}")
            
        except Exception as e:
            print(f"Erro ao processar mídia {media.sid}: {str(e)}")
            self.stats['errors'] += 1
    
    def print_stats(self):
        """Imprime estatísticas do processo."""
        print("\n" + "="*50)
        print("ESTATÍSTICAS DA RECUPERAÇÃO")
        print("="*50)
        print(f"Mensagens processadas: {self.stats['messages_processed']}")
        print(f"Mídias encontradas: {self.stats['media_found']}")
        print(f"Fotos baixadas: {self.stats['photos_downloaded']}")
        print(f"URLs atualizadas no BD: {self.stats['database_updated']}")
        print(f"Erros: {self.stats['errors']}")
        print("="*50)
    
    def run(self, days_back: int = 90):
        """Executa o processo completo de recuperação."""
        print("Iniciando recuperação de fotos do Twilio...")
        print(f"Modo: {'DRY RUN' if self.dry_run else 'EXECUÇÃO REAL'}")
        
        if self.limit:
            print(f"Limite: {self.limit} mensagens")
        
        try:
            self.process_messages(days_back)
            self.print_stats()
            
        except KeyboardInterrupt:
            print("\nProcesso interrompido pelo usuário")
            self.print_stats()
            
        finally:
            self.db.close()

def main():
    parser = argparse.ArgumentParser(description='Recuperar fotos do Twilio')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Executar em modo de teste (não faz alterações)')
    parser.add_argument('--limit', type=int, 
                       help='Limitar número de mensagens processadas')
    parser.add_argument('--days', type=int, default=90,
                       help='Número de dias para buscar no histórico (padrão: 90)')
    
    args = parser.parse_args()
    
    # Verificar credenciais
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        print("Erro: Credenciais do Twilio não configuradas")
        print("Configure TWILIO_ACCOUNT_SID e TWILIO_AUTH_TOKEN no arquivo .env")
        sys.exit(1)
    
    # Executar recuperação
    recovery = TwilioPhotoRecovery(dry_run=args.dry_run, limit=args.limit)
    recovery.run(days_back=args.days)

if __name__ == "__main__":
    main()