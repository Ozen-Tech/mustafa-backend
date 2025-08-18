#!/usr/bin/env python3
"""
Script para configurar as credenciais do Twilio e testar a conexão

Este script ajuda você a:
1. Configurar suas credenciais do Twilio
2. Testar a conexão com a API
3. Listar algumas mensagens recentes para verificar
"""

import os
from twilio.rest import Client
from datetime import datetime, timedelta

def testar_credenciais_twilio():
    print("🔧 CONFIGURAÇÃO DAS CREDENCIAIS DO TWILIO")
    print("=" * 50)
    
    print("\n📋 Para encontrar suas credenciais:")
    print("1. Acesse: https://console.twilio.com/")
    print("2. No painel principal, você verá:")
    print("   - Account SID")
    print("   - Auth Token (clique em 'Show' para ver)")
    print("3. Para o número WhatsApp Business:")
    print("   - Vá em 'Messaging' > 'Try it out' > 'Send a WhatsApp message'")
    print("   - O número aparece como 'From: whatsapp:+...'")
    
    print("\n" + "=" * 50)
    
    # Solicitar credenciais
    account_sid = input("\n📱 Digite seu TWILIO_ACCOUNT_SID: ").strip()
    auth_token = input("🔑 Digite seu TWILIO_AUTH_TOKEN: ").strip()
    whatsapp_input = input("📞 Digite seu número WhatsApp Business (ex: +5598999068855): ").strip()
    
    # Normalizar o número do WhatsApp
    if whatsapp_input:
        if not whatsapp_input.startswith('whatsapp:'):
            if whatsapp_input.startswith('+'):
                whatsapp_number = f"whatsapp:{whatsapp_input}"
            else:
                whatsapp_number = f"whatsapp:+{whatsapp_input}"
        else:
            whatsapp_number = whatsapp_input
    else:
        whatsapp_number = ""
    
    print(f"📞 Número formatado: {whatsapp_number}")
    
    if not all([account_sid, auth_token, whatsapp_number]):
        print("❌ Todas as credenciais são obrigatórias!")
        return None, None, None
    
    # Testar conexão
    print("\n🔍 Testando conexão com Twilio...")
    
    try:
        client = Client(account_sid, auth_token)
        
        # Testar com uma chamada simples
        account = client.api.accounts(account_sid).fetch()
        print(f"✅ Conexão bem-sucedida!")
        print(f"📊 Status da conta: {account.status}")
        print(f"📅 Conta criada em: {account.date_created}")
        
        # Listar algumas mensagens recentes
        print("\n📱 Buscando mensagens recentes...")
        messages = client.messages.list(limit=5)
        
        print(f"📊 Encontradas {len(messages)} mensagens recentes")
        
        for msg in messages:
            print(f"  📩 {msg.date_sent}: {msg.from_} -> {msg.to}")
            if msg.num_media and int(msg.num_media) > 0:
                print(f"    📸 Contém {msg.num_media} mídia(s)")
        
        # Salvar credenciais em arquivo .env local (opcional)
        salvar = input("\n💾 Salvar credenciais em arquivo .env local? (s/N): ").strip().lower()
        
        if salvar in ['s', 'sim', 'y', 'yes']:
            with open('.env.twilio', 'w') as f:
                f.write(f"TWILIO_ACCOUNT_SID={account_sid}\n")
                f.write(f"TWILIO_AUTH_TOKEN={auth_token}\n")
                f.write(f"TWILIO_WHATSAPP_NUMBER={whatsapp_number}\n")
            print("✅ Credenciais salvas em .env.twilio")
        
        return account_sid, auth_token, whatsapp_number
        
    except Exception as e:
        print(f"❌ Erro ao conectar com Twilio: {e}")
        print("\n🔍 Verifique se:")
        print("1. Account SID está correto")
        print("2. Auth Token está correto")
        print("3. Você tem acesso à internet")
        return None, None, None

def contar_mensagens_com_midia(account_sid, auth_token, whatsapp_number, dias=30):
    """
    Conta quantas mensagens com mídia existem
    """
    print(f"\n🔍 Contando mensagens com mídia dos últimos {dias} dias...")
    
    try:
        client = Client(account_sid, auth_token)
        data_inicio = datetime.now() - timedelta(days=dias)
        
        # Buscar mensagens recebidas
        messages = client.messages.list(
            to=whatsapp_number,
            date_sent_after=data_inicio,
            limit=1000
        )
        
        total_mensagens = len(messages)
        mensagens_com_midia = 0
        total_midias = 0
        
        for msg in messages:
            if msg.num_media and int(msg.num_media) > 0:
                mensagens_com_midia += 1
                total_midias += int(msg.num_media)
        
        print(f"📊 ESTATÍSTICAS DOS ÚLTIMOS {dias} DIAS:")
        print(f"📱 Total de mensagens: {total_mensagens}")
        print(f"📸 Mensagens com mídia: {mensagens_com_midia}")
        print(f"🖼️  Total de mídias: {total_midias}")
        
        if mensagens_com_midia > 0:
            print(f"\n✅ Encontrei {total_midias} fotos que podem ser recuperadas!")
            return True
        else:
            print(f"\n⚠️  Nenhuma mídia encontrada nos últimos {dias} dias")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao contar mensagens: {e}")
        return False

def main():
    print("🚀 CONFIGURADOR DE CREDENCIAIS TWILIO")
    
    # Testar credenciais
    account_sid, auth_token, whatsapp_number = testar_credenciais_twilio()
    
    if not all([account_sid, auth_token, whatsapp_number]):
        print("❌ Não foi possível configurar as credenciais")
        return
    
    # Contar mensagens com mídia
    print("\n" + "=" * 50)
    dias_input = input("\n📅 Quantos dias atrás verificar? (padrão: 30): ").strip()
    dias = int(dias_input) if dias_input.isdigit() else 30
    
    tem_midias = contar_mensagens_com_midia(account_sid, auth_token, whatsapp_number, dias)
    
    if tem_midias:
        print("\n🚀 PRÓXIMO PASSO:")
        print("Execute: python recuperar_fotos_twilio.py")
        print("\n💡 DICA: Use as mesmas credenciais que você acabou de testar")
    else:
        print("\n💡 DICA: Tente aumentar o número de dias ou verifique se as mensagens")
        print("foram enviadas para o número WhatsApp Business correto")

if __name__ == "__main__":
    main()