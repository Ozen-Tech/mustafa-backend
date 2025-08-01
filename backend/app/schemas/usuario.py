from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Schema compacto para exibir nos detalhes do usuário
class ContratoInfo(BaseModel):
    id: int
    nome_arquivo_original: str
    url_acesso: str
    model_config = ConfigDict(from_attributes=True)

class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=3)
    email: EmailStr
    perfil: str

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6)
    empresa_id: int
    whatsapp_number: Optional[str] = None

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
    empresa_id: int
    whatsapp_number: Optional[str] = None
    contratos: List[ContratoInfo] = []

    # <<<< A CORREÇÃO ESTÁ AQUI >>>>
    # Mantemos apenas o `model_config` e removemos a `class Config` interna.
    model_config = ConfigDict(from_attributes=True)

# --- ENUM E SCHEMAS DE TOKEN (continuam iguais) ---
class PerfilUsuario(str, Enum):
    ADMIN = "ADMIN"
    GESTOR = "GESTOR"
    OPERADOR = "OPERADOR"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
