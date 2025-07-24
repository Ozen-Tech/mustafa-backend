from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, extract
from ..db import models
from datetime import date, datetime
from typing import Optional

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

def get_fotos_by_empresa(
    db: Session, 
    empresa_id: int, 
    promotor_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    busca: Optional[str] = None
) -> list[models.FotoPromotor]:
    """Busca fotos com filtros opcionais."""
    query = db.query(models.FotoPromotor).filter(models.FotoPromotor.empresa_id == empresa_id)

    if promotor_id:
        query = query.filter(models.FotoPromotor.promotor_id == promotor_id)
    if data_inicio:
        query = query.filter(models.FotoPromotor.data_envio >= data_inicio)
    if data_fim:
        # Adiciona 1 dia para incluir o dia final completo
        query = query.filter(models.FotoPromotor.data_envio < datetime.combine(data_fim, datetime.max.time()))
    if busca:
        query = query.filter(models.FotoPromotor.legenda.ilike(f"%{busca}%"))

    return query.order_by(models.FotoPromotor.data_envio.desc()).all()

# <<<< NOVA FUNÇÃO DE KPIS AQUI >>>>
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

    # Ranking (retorna ID e contagem)
    ranking = db.query(
        models.Usuario.nome,
        func.count(models.FotoPromotor.id).label('total_fotos')
    ).join(models.Usuario, models.FotoPromotor.promotor_id == models.Usuario.id)\
    .filter(models.FotoPromotor.empresa_id == empresa_id)\
    .group_by(models.Usuario.nome)\
    .order_by(func.count(models.FotoPromotor.id).desc())\
    .limit(3).all()
    
    return {
        "fotos_hoje": fotos_hoje,
        "promotores_ativos_hoje": promotores_ativos_hoje,
        "fotos_mes": fotos_mes,
        "ranking_promotores": [{"nome": nome, "total": total} for nome, total in ranking]
    }