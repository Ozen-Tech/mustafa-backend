# backend/app/crud/foto_promotor.py

import os # << IMPORTAR OS
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, distinct, extract
from ..db import models
from datetime import date, datetime
from typing import Optional

# (sua função create_foto_registro existente permanece igual)
def create_foto_registro(db: Session, url_foto: str, nome_arquivo: str, legenda: str, promotor_id: int, empresa_id: int) -> models.FotoPromotor:
    db_foto = models.FotoPromotor(
        url_foto=url_foto,
        nome_arquivo_servidor=nome_arquivo,
        legenda=legenda,
        promotor_id=promotor_id,
        empresa_id=empresa_id
    )
    db.add(db_foto)
    db.commit()
    db.refresh(db_foto)
    return db_foto

# (sua função get_fotos_by_empresa existente permanece igual)
def get_fotos_by_empresa(
    db: Session, 
    empresa_id: int, 
    promotor_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    busca: Optional[str] = None
) -> list[models.FotoPromotor]:
    """Busca fotos com filtros opcionais."""
    query = (
         db.query(models.FotoPromotor)
         .options(joinedload(models.FotoPromotor.promotor))
         .filter(models.FotoPromotor.empresa_id == empresa_id)
    )

    if promotor_id:
        query = query.filter(models.FotoPromotor.promotor_id == promotor_id)
    if data_inicio:
        # Garante que a data/hora inicial seja o início do dia
        start_datetime = datetime.combine(data_inicio, datetime.min.time())
        query = query.filter(models.FotoPromotor.data_envio >= start_datetime)
    if data_fim:
        # Garante que a data/hora final seja o fim do dia
        end_datetime = datetime.combine(data_fim, datetime.max.time())
        query = query.filter(models.FotoPromotor.data_envio <= end_datetime)
    if busca:
        query = query.filter(models.FotoPromotor.legenda.ilike(f"%{busca}%"))

    return query.order_by(models.FotoPromotor.data_envio.desc()).all()


# (sua função get_dashboard_kpis existente permanece igual)
def get_dashboard_kpis(db: Session, empresa_id: int):
    """Calcula os KPIs para o dashboard."""
    today = date.today()
    
    fotos_hoje = db.query(func.count(models.FotoPromotor.id)).filter(
        models.FotoPromotor.empresa_id == empresa_id,
        func.date(models.FotoPromotor.data_envio) == today
    ).scalar()

    promotores_ativos_hoje = db.query(func.count(distinct(models.FotoPromotor.promotor_id))).filter(
        models.FotoPromotor.empresa_id == empresa_id,
        func.date(models.FotoPromotor.data_envio) == today
    ).scalar()
    
    fotos_mes = db.query(func.count(models.FotoPromotor.id)).filter(
        models.FotoPromotor.empresa_id == empresa_id,
        extract('month', models.FotoPromotor.data_envio) == today.month,
        extract('year', models.FotoPromotor.data_envio) == today.year
    ).scalar()

    ranking = db.query(
        models.Usuario.nome,
        func.count(models.FotoPromotor.id).label('total_fotos')
    ).join(models.Usuario, models.FotoPromotor.promotor_id == models.Usuario.id)\
    .filter(models.FotoPromotor.empresa_id == empresa_id)\
    .group_by(models.Usuario.nome)\
    .order_by(func.count(models.FotoPromotor.id).desc())\
    .limit(3).all()
    
    return {
        "fotos_hoje": fotos_hoje or 0,
        "promotores_ativos_hoje": promotores_ativos_hoje or 0,
        "fotos_mes": fotos_mes or 0,
        "ranking_promotores": [{"nome": nome, "total": total} for nome, total in ranking]
    }

# <<<<<<< NOVA FUNÇÃO ADICIONADA AQUI >>>>>>>>>
def get_foto_by_id(db: Session, foto_id: int) -> Optional[models.FotoPromotor]:
    """Busca uma única foto pelo seu ID."""
    return db.query(models.FotoPromotor).filter(models.FotoPromotor.id == foto_id).first()

# <<<<<<< NOVA FUNÇÃO ADICIONADA AQUI >>>>>>>>>
def delete_foto(db: Session, foto: models.FotoPromotor) -> None:
    """Exclui uma foto do banco de dados e seu arquivo físico."""
    # Caminho para o arquivo físico
    caminho_arquivo = f"./uploads/fotos_promotores/{foto.nome_arquivo_servidor}"
    
    # Exclui o arquivo físico, se existir
    if os.path.exists(caminho_arquivo):
        try:
            os.remove(caminho_arquivo)
        except OSError as e:
            # Logar o erro, mas continuar para deletar do DB de qualquer forma
            print(f"Erro ao deletar arquivo físico {caminho_arquivo}: {e}")

    # Exclui o registro do banco de dados
    db.delete(foto)
    db.commit()