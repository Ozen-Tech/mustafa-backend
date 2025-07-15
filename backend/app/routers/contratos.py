# backend/app/routers/contratos.py

import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

# Nossos módulos
from app.db import models
from app.db.connection import get_db
from app.crud import contrato as crud_contrato
from app.schemas import contrato as schemas_contrato
from app.dependencies import get_current_user

# --- Configuração ---
router = APIRouter(prefix="/contratos", tags=["Contratos"])
UPLOAD_DIRECTORY = "./uploads"

@router.post("/upload", response_model=schemas_contrato.Contrato)
async def upload_contrato_assinado(
    # FastAPI injeta os dados do formulário e o arquivo aqui
    file: UploadFile = File(..., description="Arquivo do contrato (.pdf, .jpg, .png)"),
    nome_promotor: str = Form(..., description="Nome completo do promotor"),
    cpf_promotor: str = Form(..., description="CPF do promotor"),
    # Dependências de segurança e banco de dados
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Endpoint para um promotor fazer o upload de um contrato assinado.
    O sistema salva o arquivo, registra no banco e o associa ao usuário logado.
    """
    # 1. Validação simples do tipo de arquivo (pode ser melhorada)
    if file.content_type not in ["application/pdf", "image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido. Apenas PDF, JPG ou PNG são permitidos.")

    # 2. Criar um nome de arquivo único e seguro para evitar sobreposições
    extensao = file.filename.split('.')[-1]
    nome_arquivo_servidor = f"{uuid.uuid4()}.{extensao}"
    caminho_completo = os.path.join(UPLOAD_DIRECTORY, nome_arquivo_servidor)

    # 3. Salvar o arquivo no disco (operação de I/O, por isso o 'async')
    try:
        with open(caminho_completo, "wb") as buffer:
            conteudo = await file.read() # Ler o arquivo
            buffer.write(conteudo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Não foi possível salvar o arquivo: {e}")

    # 4. Registrar as informações no banco de dados usando nosso CRUD
    db_contrato = crud_contrato.create_contrato(
        db=db,
        nome_promotor=nome_promotor,
        cpf_promotor=cpf_promotor,
        nome_original=file.filename,
        nome_servidor=nome_arquivo_servidor,
        caminho=caminho_completo,
        usuario_id=current_user.id,
        empresa_id=current_user.empresa_id
    )

    # 5. Criar a URL de acesso dinamicamente para o retorno da API
    # (A rota para servir esse arquivo será criada no Passo 6)
    url_acesso = f"/arquivos-contratos/{nome_arquivo_servidor}"
    
    # Montar o objeto de resposta final
    response_data = schemas_contrato.Contrato(
        id=db_contrato.id,
        nome_promotor=db_contrato.nome_promotor,
        cpf_promotor=db_contrato.cpf_promotor,
        nome_arquivo_original=db_contrato.nome_arquivo_original,
        data_upload=db_contrato.data_upload,
        usuario_id=db_contrato.usuario_id,
        url_acesso=url_acesso # Adicionando a URL acessível
    )

    return response_data