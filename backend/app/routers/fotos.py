from fastapi import APIRouter, Depends, HTTPException, status # Importar HTTPException e status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta

from app.db import models
from app.db.connection import get_db
from app.crud import foto_promotor as crud_foto
from app.schemas import foto_promotor as schemas_foto
from app.dependencies import get_current_user
from app.schemas.usuario import PerfilUsuario # Importar o Enum

router = APIRouter()

# (sua rota GET existente permanece igual)
@router.get("", response_model=List[schemas_foto.FotoPromotor])
def read_fotos_empresa(
    db: Session = Depends(get_db), 
    current_user: models.Usuario = Depends(get_current_user),
    promotor_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    busca: Optional[str] = None
):
    fotos_db = crud_foto.get_fotos_by_empresa(
        db, 
        empresa_id=current_user.empresa_id,
        promotor_id=promotor_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        busca=busca
    )

    response = [
        schemas_foto.FotoPromotor(
            **foto.__dict__, 
            nome_promotor=foto.promotor.nome
        ) for foto in fotos_db
    ]
    return response
    
    # << ATUALIZADO >> Associar o nome do promotor a cada foto
    fotos_com_promotor = []
    for foto in fotos_db:
        foto_schema = schemas_foto.FotoPromotorComPromotor.model_validate(foto)
        foto_schema.nome_promotor = foto.promotor.nome
        fotos_com_promotor.append(foto_schema)

    return fotos_com_promotor


# <<<<<<< NOVA ROTA ADICIONADA AQUI >>>>>>>>>
@router.delete("/{foto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_foto_by_id(
    foto_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Exclui uma foto. Apenas usuários com perfil ADMIN podem executar esta ação.
    """
    # 1. Verificar permissão
    if current_user.perfil != PerfilUsuario.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ação não permitida. Apenas administradores podem excluir fotos."
        )

    # 2. Buscar a foto no banco de dados
    foto_a_deletar = crud_foto.get_foto_by_id(db=db, foto_id=foto_id)

    # 3. Validar se a foto existe e pertence à empresa do usuário
    if not foto_a_deletar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto não encontrada.")
    
    if foto_a_deletar.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Foto não pertence à sua empresa.")

    # 4. Chamar o CRUD para deletar a foto
    crud_foto.delete_foto(db=db, foto=foto_a_deletar)
    
    # Retorna uma resposta vazia com status 204
    return

# <<<< NOVA ROTA DE DOWNLOAD >>>>
@router.get("/download/{promotor_id}", summary="Baixa as fotos de um promotor como ZIP")
async def download_fotos_promotor_zip(
    promotor_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Coleta as fotos dos últimos 15 dias de um promotor específico,
    compacta-as em um arquivo ZIP e o retorna para download.
    """
    data_fim = date.today()
    data_inicio = data_fim - timedelta(days=15)

    fotos = crud_foto.get_fotos_by_empresa(
        db, 
        empresa_id=current_user.empresa_id,
        promotor_id=promotor_id,
        data_inicio=data_inicio,
        data_fim=data_fim
    )

    if not fotos:
        raise HTTPException(status_code=404, detail="Nenhuma foto encontrada para este promotor no período de 15 dias.")
        
    # Cria um arquivo ZIP em memória
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for foto in fotos:
            caminho_arquivo = os.path.join(UPLOAD_DIRECTORY, foto.nome_arquivo_servidor)
            if os.path.exists(caminho_arquivo):
                # Formato do nome do arquivo no ZIP: YYYY-MM-DD_legenda.jpg
                nome_no_zip = f"{foto.data_envio.strftime('%Y-%m-%d')}_{foto.legenda or foto.id}.jpg"
                zip_file.write(caminho_arquivo, arcname=nome_no_zip)

    zip_buffer.seek(0)
    
    # Prepara o nome do arquivo para download
    nome_promotor = fotos[0].promotor.nome.replace(" ", "_")
    nome_arquivo_zip = f"evolucao_{nome_promotor}_{data_inicio}_a_{data_fim}.zip"
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={nome_arquivo_zip}"}
    )

# <<<< NOVA ROTA DE DELEÇÃO >>>>
@router.delete("/{foto_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deleta uma foto")
def delete_foto(
    foto_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Deleta um registro de foto e seu arquivo correspondente."""
    db_foto = crud_foto.delete_foto_registro(db, foto_id=foto_id, empresa_id=current_user.empresa_id)
    if not db_foto:
        raise HTTPException(status_code=404, detail="Foto não encontrada ou não pertence à sua empresa.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
