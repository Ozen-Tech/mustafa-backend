from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=3)
    email: EmailStr
    empresa_id: int
    perfil: str # 'admin', 'vendedor', 'estoquista'

class ContratoInfo(BaseModel):
    id: int
    nome_arquivo_original: str
    url_acesso: str


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
    perfil: str

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    perfil: Optional[str] = None
    whatsapp_number: Optional[str] = None
    is_active: Optional[bool] = None

class Usuario(UsuarioBase):
    id: int
    is_active: bool
    data_criacao: datetime
    perfil: str
    contratos: List[ContratoInfo] = []


    class Config:
        from_attributes = True

# Schemas para o fluxo de Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None