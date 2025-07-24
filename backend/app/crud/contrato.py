# backend/app/crud/contrato.py

from sqlalchemy.orm import Session
from ..db import models

# =============================================================
# Sua função existente (não altere)
# =============================================================
def create_contrato(
    db: Session, 
    nome_promotor: str, 
    cpf_promotor: str, 
    nome_original: str, 
    nome_servidor: str,
    caminho: str,
    usuario_id: int, 
    empresa_id: int
) -> models.Contrato:
    """Cria um novo registro de contrato no banco de dados."""
    
    db_contrato = models.Contrato(
        nome_promotor=nome_promotor,
        cpf_promotor=cpf_promotor,
        nome_arquivo_original=nome_original,
        nome_arquivo_servidor=nome_servidor,
        caminho_arquivo=caminho,
        usuario_id=usuario_id,
        empresa_id=empresa_id
    )
    db.add(db_contrato)
    db.commit()
    db.refresh(db_contrato)
    return db_contrato

# =============================================================
# <<< NOVA FUNÇÃO ADICIONADA AQUI >>>
# =============================================================
def get_contratos_by_empresa(db: Session, empresa_id: int) -> list[models.Contrato]:
    """
    Busca todos os contratos associados a uma empresa específica.

    Args:
        db (Session): A sessão do banco de dados.
        empresa_id (int): O ID da empresa para filtrar os contratos.

    Returns:
        list[models.Contrato]: Uma lista de objetos de contrato, ordenados pelo
                               mais recente primeiro.
    """
    return (
        db.query(models.Contrato)
        .filter(models.Contrato.empresa_id == empresa_id)
        .order_by(models.Contrato.data_upload.desc())
        .all()
    )