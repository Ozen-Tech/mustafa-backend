import os
import uuid
import httpx
from fastapi import APIRouter, Depends, Form, HTTPException, Response
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.crud import usuario as crud_usuario, foto_promotor as crud_foto

router = APIRouter(prefix="/webhook")

# ================== SUAS CREDENCIAIS AQUI ==================
TWILIO_ACCOUNT_SID = "AC42a464bfabee430676ecd3d55967a6d3" 
TWILIO_AUTH_TOKEN = "0b9a303a86272ba917ba50eb55c93be5"               
# ========================================================

UPLOAD_DIRECTORY = "./uploads/fotos_promotores"

@router.post("/whatsapp")
async def handle_twilio_webhook(
    From: str = Form(...),
    MediaUrl0: str = Form(None),
    NumMedia: int = Form(0),
    Body: str = Form(None),
    db: Session = Depends(get_db)
):
    print(f"--- WEBHOOK RECEBIDO --- De: {From}, Mídias: {NumMedia}")

    if NumMedia == 0 or not MediaUrl0:
        return Response(content="<?xml version='1.0' encoding='UTF-8'?><Response/>", media_type="application/xml")

    promotor = crud_usuario.get_user_by_whatsapp(db, whatsapp_number=From)
    if not promotor:
        print(f"ERRO: Promotor com o número {From} não encontrado.")
        return Response(content="<?xml version='1.0' encoding='UTF-8'?><Response/>", media_type="application/xml")

    try:
        auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # <<<<<< AQUI ESTÁ A CORREÇÃO MÁGICA! >>>>>>
        async with httpx.AsyncClient(auth=auth, follow_redirects=True) as client:
            response = await client.get(MediaUrl0)
            response.raise_for_status()
            image_bytes = response.content
            content_type = response.headers.get('content-type', 'image/jpeg')

    except httpx.HTTPStatusError as e:
        print(f"ERRO ao baixar mídia da Twilio. Status: {e.response.status_code}")
        raise HTTPException(status_code=500, detail="Não foi possível baixar a imagem da Twilio.")

    # O resto do código já estava perfeito
    extensao = content_type.split('/')[-1] if '/' in content_type else 'jpg'
    if extensao not in ['jpg', 'jpeg', 'png']: extensao = 'jpg'
    
    nome_arquivo_servidor = f"{uuid.uuid4()}.{extensao}"
    caminho_completo = os.path.join(UPLOAD_DIRECTORY, nome_arquivo_servidor)
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    with open(caminho_completo, "wb") as buffer:
        buffer.write(image_bytes)
    
    url_acesso_foto = f"/fotos-promotores/{nome_arquivo_servidor}"
    crud_foto.create_foto_registro(db=db, url_foto=url_acesso_foto, nome_arquivo=nome_arquivo_servidor, legenda=Body, promotor_id=promotor.id, empresa_id=promotor.empresa_id)

    print(f"SUCESSO: Foto de {promotor.nome} ({From}) salva como {nome_arquivo_servidor}.")
    return Response(content="<?xml version='1.0' encoding='UTF-8'?><Response/>", media_type="application/xml")
