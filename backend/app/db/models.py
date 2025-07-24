from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base
from datetime import datetime
import uuid

class Empresa(Base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True)
    cnpj = Column(String, unique=True, index=True, nullable=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    usuarios = relationship("Usuario", back_populates="empresa")
    contratos = relationship("Contrato", back_populates="empresa")
    fotos_enviadas = relationship("FotoPromotor", back_populates="empresa")

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    whatsapp_number = Column(String, unique=True, index=True, nullable=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    perfil = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())
    empresa = relationship("Empresa", back_populates="usuarios")
    contratos = relationship("Contrato", back_populates="usuario")
    fotos_enviadas = relationship("FotoPromotor", back_populates="promotor")

class FotoPromotor(Base):
    __tablename__ = "fotos_promotores"

    id = Column(Integer, primary_key=True, index=True)
    url_foto = Column(String, nullable=False) # URL pública da imagem salva
    nome_arquivo_servidor = Column(String, nullable=False, unique=True)
    legenda = Column(String, nullable=True) # Texto que veio junto com a foto
    
    # Contexto do envio (extraído da legenda pela IA ou pelo promotor)
    loja = Column(String, index=True, nullable=True)
    cidade = Column(String, index=True, nullable=True)
    
    # Data e Relacionamentos
    data_envio = Column(DateTime(timezone=True), server_default=func.now())
    promotor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)

    promotor = relationship("Usuario", back_populates="fotos_enviadas")
    empresa = relationship("Empresa")

class Contrato(Base):
    __tablename__ = "contratos"

    id = Column(Integer, primary_key=True, index=True)
    nome_promotor = Column(String, nullable=False, index=True)
    cpf_promotor = Column(String, nullable=False, index=True)

    nome_arquivo_original = Column(String, nullable=False)
    nome_arquivo_servidor = Column(String, nullable=False, unique=True) # Nome único para evitar conflitos
    caminho_arquivo = Column(String, nullable=False)
    
    data_upload = Column(DateTime(timezone=True), server_default=func.now())

    # --- Relacionamentos para saber QUEM fez o upload e de QUAL EMPRESA ---
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)

    usuario = relationship("Usuario") # Podemos chamar contrato.usuario
    empresa = relationship("Empresa") # Podemos chamar contrato.empresa
