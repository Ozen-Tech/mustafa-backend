#!/usr/bin/env python3
"""
Script para recuperar todas as fotos do Twilio e atualizar o banco de dados

Este script:
1. Conecta à API do Twilio
2. Busca todas as mensagens com mídia (fotos)
3. Atualiza o banco de dados com as URLs corretas do Twilio
4. Associa as fotos aos promotores corretos

INFORMAÇÕES NECESSÁRIAS:
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- Número do WhatsApp Business (formato: whatsapp:+5511999999999)
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from twilio.rest import Client
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Adicionar o diretório backend ao path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Mudar para o diretório backend para importações funcionarem
os.chdir(backend_path)

from app.core.config import settings
from app.db.models import FotoPromotor, Usuario
from app.db.session import SessionLocal

class TwilioPhotoRecovery:
    def __init__(self):
        # Configurações do Twilio (você precisa fornecer estas informações)
        self.account_sid = input("Digite seu TWILIO_ACCOUNT_SID: ").strip()
        self.auth_token = input("Digite seu TWILIO_AUTH_TOKEN: ").strip()
        self.whatsapp_number = input("Digite seu número WhatsApp Business (ex: whatsapp:+5511999999999): ").strip()
        
        if not all([self.account_sid, self.auth_token, self.whatsapp_number]):
            raise ValueError("Todas as credenciais do Twilio são obrigatórias!")
        
        self.client = Client(self.account_sid, self.auth_token)
        self.db = SessionLocal()
        
        # Estatísticas
        self.stats = {
            'mensagens_encontradas': 0,
            'fotos_encontradas': 0,
            'fotos_atualizadas': 0,
            'promotores_encontrados': 0,
            'erros': 0
        }
    
    def buscar_mensagens_com_midia(self, dias_atras: int = 365) -> List[Dict]:
        """
        Busca todas as mensagens com mídia dos últimos X dias
        """
        print(f"🔍 Buscando mensagens com mídia dos últimos {dias_atras} dias...")
        
        data_inicio = datetime.now() - timedelta(days=dias_atras)
        mensagens_com_midia = []
        
        try:
            # Buscar mensagens recebidas (de promotores para você)
            messages = self.client.messages.list(
                to=self.whatsapp_number,
                date_sent_after=data_inicio,
                limit=2000  # Ajuste conforme necessário
            )
            
            print(f"📱 Encontradas {len(messages)} mensagens no total")
            
            for message in messages:
                self.stats['mensagens_encontradas'] += 1
                
                # Verificar se a mensagem tem mídia
                if message.num_media and int(message.num_media) > 0:
                    # Buscar detalhes da mídia
                    media_list = self.client.messages(message.sid).media.list()
                    
                    for media in media_list:
                        if media.content_type and media.content_type.startswith('image/'):
                            mensagens_com_midia.append({
                                'message_sid': message.sid,
                                'media_sid': media.sid,
                                'media_url': f"https://api.twilio.com{media.uri.replace('.json', '')}",
                                'content_type': media.content_type,
                                'from_number': message.from_,
                                'date_sent': message.date_sent,
                                'body': message.body or ''
                            })
                            self.stats['fotos_encontradas'] += 1
            
            print(f"📸 Encontradas {len(mensagens_com_midia)} fotos")
            return mensagens_com_midia
            
        except Exception as e:
            print(f"❌ Erro ao buscar mensagens: {e}")
            self.stats['erros'] += 1
            return []
    
    def encontrar_promotor_por_numero(self, numero_whatsapp: str) -> Optional[Usuario]:
        """
        Encontra um promotor pelo número do WhatsApp
        """
        # Limpar o número (remover whatsapp: e caracteres especiais)
        numero_limpo = numero_whatsapp.replace('whatsapp:', '').replace('+', '').replace('-', '').replace(' ', '')
        
        # Buscar promotor no banco
        promotor = self.db.query(Usuario).filter(
            Usuario.whatsapp_number.ilike(f"%{numero_limpo[-10:]}%")  # Últimos 10 dígitos
        ).first()
        
        if promotor:
            self.stats['promotores_encontrados'] += 1
        
        return promotor
    
    def atualizar_foto_no_banco(self, foto_info: Dict, promotor: Usuario) -> bool:
        """
        Atualiza ou cria uma foto no banco de dados
        """
        try:
            # Verificar se já existe uma foto com esta URL
            foto_existente = self.db.query(FotoPromotor).filter(
                FotoPromotor.url == foto_info['media_url']
            ).first()
            
            if foto_existente:
                print(f"📸 Foto já existe no banco: {foto_info['media_sid']}")
                return False
            
            # Criar nova foto
            nova_foto = FotoPromotor(
                url=foto_info['media_url'],
                filename=f"{foto_info['media_sid']}.jpg",
                caption=foto_info['body'][:500] if foto_info['body'] else '',
                promotor_id=promotor.id,
                empresa_id=promotor.empresa_id,
                data_upload=foto_info['date_sent']
            )
            
            self.db.add(nova_foto)
            self.db.commit()
            
            self.stats['fotos_atualizadas'] += 1
            print(f"✅ Foto salva: {foto_info['media_sid']} - Promotor: {promotor.nome}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar foto {foto_info['media_sid']}: {e}")
            self.db.rollback()
            self.stats['erros'] += 1
            return False
    
    def processar_recuperacao(self, dias_atras: int = 365):
        """
        Processo principal de recuperação
        """
        print("🚀 INICIANDO RECUPERAÇÃO DE FOTOS DO TWILIO")
        print("=" * 50)
        
        # 1. Buscar mensagens com mídia
        mensagens_com_midia = self.buscar_mensagens_com_midia(dias_atras)
        
        if not mensagens_com_midia:
            print("❌ Nenhuma foto encontrada no Twilio")
            return
        
        # 2. Processar cada foto
        print(f"\n📝 Processando {len(mensagens_com_midia)} fotos...")
        
        for i, foto_info in enumerate(mensagens_com_midia, 1):
            print(f"\n🔄 [{i}/{len(mensagens_com_midia)}] Processando foto {foto_info['media_sid']}...")
            
            # Encontrar promotor
            promotor = self.encontrar_promotor_por_numero(foto_info['from_number'])
            
            if not promotor:
                print(f"⚠️  Promotor não encontrado para número: {foto_info['from_number']}")
                continue
            
            # Atualizar foto no banco
            self.atualizar_foto_no_banco(foto_info, promotor)
        
        # 3. Mostrar estatísticas finais
        self.mostrar_estatisticas()
    
    def mostrar_estatisticas(self):
        """
        Mostra estatísticas da recuperação
        """
        print("\n" + "=" * 50)
        print("📊 ESTATÍSTICAS DA RECUPERAÇÃO:")
        print(f"📱 Mensagens analisadas: {self.stats['mensagens_encontradas']}")
        print(f"📸 Fotos encontradas no Twilio: {self.stats['fotos_encontradas']}")
        print(f"✅ Fotos salvas no banco: {self.stats['fotos_atualizadas']}")
        print(f"👤 Promotores encontrados: {self.stats['promotores_encontrados']}")
        print(f"❌ Erros: {self.stats['erros']}")
        print("=" * 50)
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

def main():
    print("🔧 RECUPERADOR DE FOTOS DO TWILIO")
    print("=" * 40)
    print("\n📋 INFORMAÇÕES NECESSÁRIAS:")
    print("1. TWILIO_ACCOUNT_SID (encontre no Console do Twilio)")
    print("2. TWILIO_AUTH_TOKEN (encontre no Console do Twilio)")
    print("3. Número WhatsApp Business (formato: whatsapp:+5511999999999)")
    print("\n⚠️  IMPORTANTE: Este script irá buscar fotos dos últimos 365 dias")
    print("\n" + "=" * 40)
    
    try:
        recovery = TwilioPhotoRecovery()
        
        # Perguntar quantos dias buscar
        dias_input = input("\nQuantos dias atrás buscar? (padrão: 365): ").strip()
        dias_atras = int(dias_input) if dias_input.isdigit() else 365
        
        # Confirmar antes de executar
        confirmar = input(f"\n🚀 Buscar fotos dos últimos {dias_atras} dias? (s/N): ").strip().lower()
        
        if confirmar in ['s', 'sim', 'y', 'yes']:
            recovery.processar_recuperacao(dias_atras)
        else:
            print("❌ Operação cancelada")
            
    except KeyboardInterrupt:
        print("\n❌ Operação interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()