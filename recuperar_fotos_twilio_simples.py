#!/usr/bin/env python3
"""
Script simplificado para recuperar fotos do Twilio
"""

import os
from datetime import datetime, timedelta
from twilio.rest import Client
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

def carregar_credenciais():
    """Carrega credenciais do arquivo .env.twilio"""
    if os.path.exists('.env.twilio'):
        credenciais = {}
        with open('.env.twilio', 'r') as f:
            for linha in f:
                if '=' in linha:
                    chave, valor = linha.strip().split('=', 1)
                    credenciais[chave] = valor
        return credenciais
    return None

def conectar_banco():
    """Conecta ao banco de dados"""
    # URL do banco (mesma do seu sistema)
    database_url = "postgresql://mustafa_postgres_user:QxeSnBvaMTDhKKX106LX9whiau27pgfM@dpg-d20psdemcj7s73e18tag-a.oregon-postgres.render.com/mustafa_postgres"
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session(), engine

def buscar_promotores(session):
    """Busca todos os operadores no banco"""
    result = session.execute(text("""
        SELECT id, nome, whatsapp_number, empresa_id 
        FROM usuarios 
        WHERE perfil = 'OPERADOR'
    """))
    
    promotores = {}
    for row in result:
        numero_limpo = str(row.whatsapp_number or '').replace('+', '').replace('-', '').replace(' ', '')
        if len(numero_limpo) >= 10:
            # Usar os últimos 10 dígitos como chave
            chave = numero_limpo[-10:]
            promotores[chave] = {
                'id': row.id,
                'nome': row.nome,
                'whatsapp_number': row.whatsapp_number,
                'empresa_id': row.empresa_id
            }
    
    return promotores

def recuperar_fotos_twilio():
    print("🚀 RECUPERADOR SIMPLIFICADO DE FOTOS DO TWILIO")
    print("=" * 50)
    
    # 1. Carregar credenciais
    credenciais = carregar_credenciais()
    if not credenciais:
        print("❌ Arquivo .env.twilio não encontrado!")
        print("Execute primeiro: python configurar_credenciais_twilio.py")
        return
    
    account_sid = credenciais.get('TWILIO_ACCOUNT_SID')
    auth_token = credenciais.get('TWILIO_AUTH_TOKEN')
    whatsapp_number = credenciais.get('TWILIO_WHATSAPP_NUMBER')
    
    print(f"📱 Usando número: {whatsapp_number}")
    
    # 2. Conectar ao Twilio
    client = Client(account_sid, auth_token)
    
    # 3. Conectar ao banco
    session, engine = conectar_banco()
    print("✅ Conectado ao banco de dados")
    
    # 4. Buscar promotores
    promotores = buscar_promotores(session)
    print(f"👥 Encontrados {len(promotores)} promotores")
    
    # 5. Buscar mensagens com mídia
    dias_atras = int(input("\n📅 Quantos dias atrás buscar? (padrão: 30): ") or "30")
    data_inicio = datetime.now() - timedelta(days=dias_atras)
    
    print(f"\n🔍 Buscando mensagens dos últimos {dias_atras} dias...")
    
    messages = client.messages.list(
        to=whatsapp_number,
        date_sent_after=data_inicio,
        limit=2000
    )
    
    print(f"📱 Encontradas {len(messages)} mensagens")
    
    # 6. Processar mensagens com mídia
    fotos_processadas = 0
    fotos_salvas = 0
    promotores_nao_encontrados = set()
    
    for i, message in enumerate(messages, 1):
        if message.num_media and int(message.num_media) > 0:
            print(f"\n🔄 [{i}/{len(messages)}] Processando mensagem {message.sid}...")
            
            # Encontrar promotor
            numero_from = message.from_.replace('whatsapp:', '').replace('+', '')
            chave_promotor = numero_from[-10:] if len(numero_from) >= 10 else numero_from
            
            promotor = promotores.get(chave_promotor)
            
            if not promotor:
                promotores_nao_encontrados.add(message.from_)
                print(f"⚠️  Promotor não encontrado para: {message.from_}")
                continue
            
            # Buscar mídia da mensagem
            media_list = client.messages(message.sid).media.list()
            
            for media in media_list:
                if media.content_type and media.content_type.startswith('image/'):
                    fotos_processadas += 1
                    
                    # URL da mídia
                    media_url = f"https://api.twilio.com{media.uri.replace('.json', '')}"
                    
                    # Verificar se já existe
                    existe = session.execute(text("""
                        SELECT id FROM fotos_promotores WHERE url_foto = :url
                    """), {'url': media_url}).fetchone()
                    
                    if existe:
                        print(f"📸 Foto já existe: {media.sid}")
                        continue
                    
                    # Salvar no banco
                    try:
                        session.execute(text("""
                            INSERT INTO fotos_promotores (url_foto, nome_arquivo_servidor, legenda, promotor_id, empresa_id, data_envio)
                            VALUES (:url_foto, :nome_arquivo_servidor, :legenda, :promotor_id, :empresa_id, :data_envio)
                        """), {
                            'url_foto': media_url,
                            'nome_arquivo_servidor': f"{media.sid}.jpg",
                            'legenda': (message.body or '')[:500],
                            'promotor_id': promotor['id'],
                            'empresa_id': promotor['empresa_id'],
                            'data_envio': message.date_sent
                        })
                        
                        session.commit()
                        fotos_salvas += 1
                        print(f"✅ Foto salva: {media.sid} - {promotor['nome']}")
                        
                    except Exception as e:
                        print(f"❌ Erro ao salvar foto {media.sid}: {e}")
                        session.rollback()
    
    # 7. Estatísticas finais
    print("\n" + "=" * 50)
    print("📊 ESTATÍSTICAS FINAIS:")
    print(f"📱 Mensagens analisadas: {len(messages)}")
    print(f"📸 Fotos processadas: {fotos_processadas}")
    print(f"✅ Fotos salvas no banco: {fotos_salvas}")
    print(f"👥 Promotores cadastrados: {len(promotores)}")
    
    if promotores_nao_encontrados:
        print(f"\n⚠️  Números não encontrados ({len(promotores_nao_encontrados)}):")
        for numero in list(promotores_nao_encontrados)[:5]:  # Mostrar apenas os primeiros 5
            print(f"   {numero}")
        if len(promotores_nao_encontrados) > 5:
            print(f"   ... e mais {len(promotores_nao_encontrados) - 5}")
    
    print("=" * 50)
    print(f"🎉 RECUPERAÇÃO CONCLUÍDA! {fotos_salvas} fotos adicionadas ao sistema!")
    
    session.close()

if __name__ == "__main__":
    try:
        recuperar_fotos_twilio()
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")