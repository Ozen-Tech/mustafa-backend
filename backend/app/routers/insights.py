from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
from app.db.connection import get_db
from app.dependencies import get_current_user
from app.services import ai_service
from app.db import models
from app.crud import foto_promotor as crud_foto
from pydantic import BaseModel
from typing import List


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

@router.post("/ask")
def ask_ai_question(
     request: QuestionRequest,
     db: Session = Depends(get_db),
     current_user: models.Usuario = Depends(get_current_user)
 ):
     # 1. Coletar os dados das fotos para dar contexto à IA
     fotos = crud_foto.get_fotos_by_empresa(db=db, empresa_id=current_user.empresa_id)
     
     # 2. Formatar os dados em um JSON legível
     data_for_ai = {
         "registros_fotos": [
             {
                 "id_foto": f.id,
                 "id_promotor": f.promotor_id,
                 "nome_promotor": f.promotor.nome,
                 "data_envio": f.data_envio.isoformat(),
                 "legenda_original": f.legenda,
                 "loja_identificada": f.loja, # Adicionar lógica para extrair isso
                 "cidade_identificada": f.cidade # da legenda se necessário
             } 
             for f in fotos
         ]
     }
     system_data_json = json.dumps(data_for_ai, default=str, indent=2)

     # 3. Chamar o serviço de IA com a pergunta do usuário e os dados coletados
     answer = ai_service.generate_analysis_from_data(
         user_question=request.question,
         system_data=system_data_json
     )
     
     return {"answer": answer, "question": request.question}
     