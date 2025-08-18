import os
import uuid
import httpx
import logging
from fastapi import APIRouter, Depends, Form, Response, BackgroundTasks
from sqlalchemy.orm import Session

# Importações dos seus próprios módulos
from app.db.connection import SessionLocal # Usaremos para criar sessões independentes para as tasks
from app.crud import usuario as crud_usuario, foto_promotor as crud_foto
from app.core.config import settings

# Configura um logger para que você possa ver saídas detalhadas nos logs da Render
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook")

# O diretório onde as fotos serão salvas.
# Lembre-se da natureza efêmera deste armazenamento na Render!
UPLOAD_DIRECTORY = "./uploads/fotos_promotores"


def process_foto_whatsapp(from_number: str, media_url: str, caption: str):
    """
    Processa a foto recebida via WhatsApp em uma tarefa de fundo.
    
    Esta função é executada de forma independente, após a resposta já ter sido
    enviada para a Twilio. Ela cria sua própria sessão de banco de dados para
    garantir que a operação seja segura e não interfira com outras requisições.
    
    Agora usa apenas URLs do Twilio, sem fazer upload para serviços externos.
    """
    logger.info(f"TASK INICIADA: Processando foto para o número {from_number}")
    db: Session = SessionLocal()  # Cria uma nova sessão de DB exclusiva para esta tarefa

    try:
        # 1. Encontrar o promotor pelo número de WhatsApp
        promotor = crud_usuario.get_user_by_whatsapp(db, whatsapp_number=from_number)
        if not promotor:
            logger.error(f"TASK ERRO: Promotor com o número {from_number} não foi encontrado no banco de dados.")
            return  # Encerra a tarefa se o promotor não existir

        logger.info(f"TASK INFO: Promotor encontrado: {promotor.nome} (ID: {promotor.id})")

        # 2. Verificar se a URL da mídia do Twilio está acessível
        auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Fazemos uma verificação HEAD para confirmar que a mídia existe
        with httpx.Client(auth=auth, follow_redirects=True) as client:
            logger.info(f"TASK INFO: Verificando mídia em {media_url}")
            response = client.head(media_url)
            response.raise_for_status()  # Lança uma exceção se o status não for 2xx
            
            content_type = response.headers.get('content-type', 'image/jpeg')
            logger.info(f"TASK INFO: Mídia verificada com sucesso. Tipo: {content_type}")

        # 3. Gerar um nome único para identificação
        extensao = content_type.split('/')[-1] if '/' in content_type else 'jpg'
        if extensao.lower() not in ['jpg', 'jpeg', 'png']:
            extensao = 'jpg'  # Garante uma extensão padrão
        
        nome_arquivo_servidor = f"{uuid.uuid4()}.{extensao}"
        
        logger.info(f"TASK INFO: Usando URL direta do Twilio: {media_url}")
        
        # 4. Registrar a foto no banco de dados usando a URL do Twilio
        crud_foto.create_foto_registro(
            db=db,
            url_foto=media_url,  # URL direta do Twilio
            nome_arquivo=nome_arquivo_servidor,  # Nome único gerado
            legenda=caption,
            promotor_id=promotor.id,
            empresa_id=promotor.empresa_id
        )

        logger.info(f"TASK SUCESSO: Foto de {promotor.nome} ({from_number}) foi registrada no banco de dados com URL do Twilio.")

    except httpx.HTTPStatusError as e:
        logger.error(f"TASK ERRO: Falha ao verificar mídia da Twilio. Status: {e.response.status_code}. Resposta: {e.response.text}")
    except Exception as e:
        # Pega qualquer outro erro inesperado e o registra detalhadamente
        logger.error(f"TASK ERRO: Falha inesperada ao processar a foto. Erro: {e}", exc_info=True)
    finally:
        # 5. Fechar a sessão do banco de dados
        # É CRUCIAL fechar a sessão para liberar a conexão de volta para o pool.
        db.close()
        logger.info(f"TASK FINALIZADA para o número {from_number}")


@router.post("/whatsapp")
async def handle_twilio_webhook(
    background_tasks: BackgroundTasks,  # Injeta o gerenciador de tarefas de fundo
    From: str = Form(...),
    MediaUrl0: str = Form(None),
    NumMedia: int = Form(0),
    Body: str = Form(None),
):
    """
    Recebe o webhook da Twilio, responde imediatamente com 200 OK,
    e agenda o processamento da imagem para ocorrer em segundo plano.
    """
    logger.info(f"WEBHOOK RECEBIDO: De: {From}, Mídias: {NumMedia}, Corpo: '{Body}'")

    # Se a mensagem contiver mídia, agendamos a tarefa de processamento
    if NumMedia > 0 and MediaUrl0:
        background_tasks.add_task(process_foto_whatsapp, From, MediaUrl0, Body)
        logger.info(f"Tarefa de processamento de foto para {From} foi adicionada à fila.")
    else:
        logger.info("Webhook recebido sem mídia. Nenhuma tarefa agendada.")

    # Retorna a resposta vazia para a Twilio IMEDIATAMENTE.
    # Isso garante que a Twilio sempre receba um 200 OK e não dê timeout.
    return Response(content="<?xml version='1.0' encoding='UTF-8'?><Response/>", media_type="application/xml")