# backend/app/routers/fotos.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.db import models
from app.db.connection import get_db
from app.crud import foto_promotor as crud_foto
from app.schemas import foto_promotor as schemas_foto
from app.dependencies import get_current_user

router = APIRouter()

@router.get("", response_model=List[schemas_foto.FotoPromotor])
def read_fotos_empresa(
    db: Session = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user),
    # Parâmetros de filtro
    promotor_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    busca: Optional[str] = None
):
    return crud_foto.get_fotos_by_empresa(
        db, 
        empresa_id=current_user.empresa_id,
        promotor_id=promotor_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        busca=busca
    )