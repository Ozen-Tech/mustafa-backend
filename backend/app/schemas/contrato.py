# backend/app/schemas/contrato.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Schema para dados que vêm do banco (retorno da API)
class Contrato(BaseModel):
    id: int
    nome_promotor: str
    cpf_promotor: str
    nome_arquivo_original: str
    url_acesso: str  # Vamos gerar a URL acessível dinamicamente
    data_upload: datetime
    usuario_id: int

    # Configuração para ler de um modelo SQLAlchemy
    model_config = ConfigDict(from_attributes=True)