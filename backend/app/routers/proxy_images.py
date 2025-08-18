from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
import requests
from twilio.rest import Client
from app.core.config import settings
import io
from urllib.parse import urlparse

router = APIRouter()

@router.get("/twilio-image/{account_sid}/{message_sid}/{media_sid}")
async def proxy_twilio_image(account_sid: str, message_sid: str, media_sid: str):
    """
    Proxy para servir imagens do Twilio com autenticação.
    
    Esta rota recebe os parâmetros da URL do Twilio e busca a imagem
    usando as credenciais configuradas, retornando-a para o frontend.
    """
    try:
        # Verificar se as credenciais do Twilio estão configuradas
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            raise HTTPException(status_code=500, detail="Credenciais do Twilio não configuradas")
        
        # Construir a URL da mídia do Twilio
        twilio_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages/{message_sid}/Media/{media_sid}"
        
        # Fazer a requisição autenticada para o Twilio
        response = requests.get(
            twilio_url,
            auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
            timeout=30
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Imagem não encontrada no Twilio")
        
        # Determinar o tipo de conteúdo
        content_type = response.headers.get('content-type', 'image/jpeg')
        
        # Retornar a imagem como streaming response
        return StreamingResponse(
            io.BytesIO(response.content),
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=3600",  # Cache por 1 hora
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar imagem: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/image-proxy")
async def proxy_image_by_url(url: str):
    """
    Proxy genérico para imagens do Twilio baseado na URL completa.
    
    Recebe uma URL completa do Twilio e a serve com autenticação.
    """
    try:
        # Verificar se é uma URL do Twilio
        if "api.twilio.com" not in url:
            raise HTTPException(status_code=400, detail="URL não é do Twilio")
        
        # Verificar credenciais
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            raise HTTPException(status_code=500, detail="Credenciais do Twilio não configuradas")
        
        # Fazer a requisição autenticada
        response = requests.get(
            url,
            auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
            timeout=30
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Imagem não encontrada")
        
        # Determinar o tipo de conteúdo
        content_type = response.headers.get('content-type', 'image/jpeg')
        
        # Retornar a imagem
        return StreamingResponse(
            io.BytesIO(response.content),
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*"
            }
        )
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar imagem: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")