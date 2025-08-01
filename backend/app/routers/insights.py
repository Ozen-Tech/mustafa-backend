# backend/app/routers/insights.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
import json
from pydantic import BaseModel
from typing import List
from datetime import date, timedelta
from app.db.connection import get_db
from app.dependencies import get_current_user
from app.services import ai_service
from app.db import models
from app.crud import foto_promotor as crud_foto

class RankingItem(BaseModel):
    nome: str
    total: int

class KPISchema(BaseModel):
    fotos_hoje: int
    promotores_ativos_hoje: int
    fotos_mes: int
    ranking_promotores: List[RankingItem]

router = APIRouter(tags=["Insights e KPIs"])

@router.get("/kpis", response_model=KPISchema)
def get_kpis(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Retorna os KPIs para o dashboard principal."""
    return crud_foto.get_dashboard_kpis(db, empresa_id=current_user.empresa_id)

class QuestionRequest(BaseModel):
    question: str
    # Opcional: filtros para dar um contexto mais específico para a IA
    promotor_id: int | None = None
    data_inicio: str | None = None
    data_fim: str | None = None

@router.post("/ask", summary="Faça uma pergunta para a IA sobre os dados de fotos")
def ask_ai_question(
     request: QuestionRequest,
     db: Session = Depends(get_db),
     current_user: models.Usuario = Depends(get_current_user)
 ):
    # <<<< LÓGICA DE BUSCA DE DADOS MELHORADA >>>>
    # Por padrão, vamos buscar os dados da última semana para dar mais contexto à IA.
    data_fim = date.today()
    data_inicio = data_fim - timedelta(days=7)

    fotos = crud_foto.get_fotos_by_empresa(
        db=db, 
        empresa_id=current_user.empresa_id,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    
    # <<<< ESTRUTURA DE DADOS ENRIQUECIDA >>>>
    data_for_ai = {
        "contexto_analise": {
            "periodo_dados": f"De {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
            "objetivo": "Analisar a atividade e os padrões de visita dos promotores de vendas com base nas fotos e legendas enviadas por eles."
        },
        "registros_fotos": [
            {
                "id_foto": f.id,
                "nome_promotor": f.promotor.nome,
                "data_envio": f.data_envio.isoformat(),
                "legenda_original": f.legenda,
                "loja_identificada": f.loja,
                "cidade_identificada": f.cidade
            } for f in fotos
        ]
    }
    system_data_json = json.dumps(data_for_ai, default=str, indent=2)

    answer = ai_service.generate_analysis_from_data(
        user_question=request.question,
        system_data=system_data_json
    )
    
    return {"answer": answer, "question": request.question}