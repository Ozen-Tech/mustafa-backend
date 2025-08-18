#!/usr/bin/env python3
"""
Script para verificar a estrutura da tabela de fotos
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

def verificar_tabela_fotos():
    print("🔍 VERIFICANDO TABELA DE FOTOS")
    print("=" * 40)
    
    session, engine = conectar_banco()
    
    # Verificar colunas da tabela fotos_promotores
    result = session.execute(text("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'fotos_promotores'
        ORDER BY ordinal_position
    """))
    
    print("📋 Colunas da tabela 'fotos_promotores':")
    for row in result:
        nullable = "NULL" if row.is_nullable == "YES" else "NOT NULL"
        print(f"   {row.column_name}: {row.data_type} ({nullable})")
    
    # Contar registros existentes
    result = session.execute(text("SELECT COUNT(*) as total FROM fotos_promotores"))
    total_fotos = result.fetchone().total
    print(f"\n📸 Total de fotos existentes: {total_fotos}")
    
    # Mostrar alguns exemplos
    if total_fotos > 0:
        result = session.execute(text("SELECT * FROM fotos_promotores LIMIT 3"))
        print("\n📋 Exemplos de registros:")
        for i, row in enumerate(result, 1):
            print(f"   Registro {i}: {dict(row._mapping)}")
    
    session.close()

if __name__ == "__main__":
    verificar_tabela_fotos()