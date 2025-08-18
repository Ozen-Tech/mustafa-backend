#!/usr/bin/env python3
"""
Script para verificar usuários no banco de dados
"""

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

def conectar_banco():
    """Conecta ao banco de dados"""
    database_url = "postgresql://mustafa_postgres_user:QxeSnBvaMTDhKKX106LX9whiau27pgfM@dpg-d20psdemcj7s73e18tag-a.oregon-postgres.render.com/mustafa_postgres"
    
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session(), engine

def verificar_usuarios():
    print("🔍 VERIFICANDO USUÁRIOS NO BANCO")
    print("=" * 40)
    
    session, engine = conectar_banco()
    
    # Total de usuários
    result = session.execute(text('SELECT COUNT(*) as total FROM usuarios'))
    total_usuarios = result.fetchone().total
    print(f"👥 Total de usuários: {total_usuarios}")
    
    # Perfis distintos
    result = session.execute(text('SELECT DISTINCT perfil FROM usuarios'))
    perfis = [row.perfil for row in result]
    print(f"🏷️  Perfis encontrados: {perfis}")
    
    # Contagem por perfil
    for perfil in perfis:
        result = session.execute(text('SELECT COUNT(*) as total FROM usuarios WHERE perfil = :perfil'), {'perfil': perfil})
        count = result.fetchone().total
        print(f"   {perfil}: {count} usuários")
    
    # Verificar se existe campo whatsapp_number
    try:
        result = session.execute(text('SELECT COUNT(*) FROM usuarios WHERE whatsapp_number IS NOT NULL'))
        com_whatsapp = result.fetchone()[0]
        print(f"📱 Usuários com WhatsApp: {com_whatsapp}")
        
        # Mostrar alguns exemplos
        if com_whatsapp > 0:
            result = session.execute(text('SELECT nome, whatsapp_number, perfil FROM usuarios WHERE whatsapp_number IS NOT NULL LIMIT 5'))
            print("\n📋 Exemplos de usuários com WhatsApp:")
            for row in result:
                print(f"   {row.nome} - {row.whatsapp_number} ({row.perfil})")
                
    except Exception as e:
        print(f"❌ Erro ao verificar WhatsApp: {e}")
    
    session.close()

if __name__ == "__main__":
    verificar_usuarios()