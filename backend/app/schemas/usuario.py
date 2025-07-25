from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=3)
    email: EmailStr
    empresa_id: int
    perfil: PerfilUsuario

class ContratoInfo(BaseModel):
    id: int
    nome_arquivo_original: str
    url_acesso: str

    model_config = ConfigDict(from_attributes=True)


class PerfilUsuario(str, Enum):
    ADMIN = "ADMIN"
    GESTOR = "GESTOR"
    OPERADOR = "OPERADOR"

class UsuarioCreate(UsuarioBase):
    email: EmailStr
    password: str = Field(..., min_length=6)    
    nome: str
    empresa_id: int
    whatsapp_number: Optional[str] = None # Permitir criar com whats
    empresa_id: int = Field(default=1)   

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    perfil: Optional[PerfilUsuario] = None
    whatsapp_number: Optional[str] = None
    is_active: Optional[bool] = None

    # model_config foi substituído por Config no Pydantic V1, mas V2 usa model_config
    model_config = ConfigDict(exclude_unset=True)

class Usuario(UsuarioBase):
    id: int
    is_active: bool
    data_criacao: datetime
    empresa_id: int
    whatsapp_number: Optional[str] = None
    # << ATUALIZADO >> Aninha os contratos na resposta do usuário
    contratos: List[ContratoInfo] = []

    model_config = ConfigDict(from_attributes=True)


    class Config:
        from_attributes = True

# Schemas para o fluxo de Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None