# backend/app/crud/contrato.py

from sqlalchemy.orm import Session
from ..db import models

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