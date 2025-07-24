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

        # 2. Baixar a imagem da Twilio de forma segura
        auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Usamos um cliente síncrono aqui, pois a tarefa já está em um thread/processo de fundo
        with httpx.Client(auth=auth, follow_redirects=True) as client:
            logger.info(f"TASK INFO: Baixando mídia de {media_url}")
            response = client.get(media_url)
            response.raise_for_status()  # Lança uma exceção se o status não for 2xx
            
            image_bytes = response.content
            content_type = response.headers.get('content-type', 'image/jpeg')
            logger.info(f"TASK INFO: Mídia baixada com sucesso. Tipo: {content_type}, Tamanho: {len(image_bytes)} bytes")

        # 3. Preparar e salvar o arquivo no disco
        extensao = content_type.split('/')[-1] if '/' in content_type else 'jpg'
        if extensao.lower() not in ['jpg', 'jpeg', 'png']:
            extensao = 'jpg'  # Garante uma extensão padrão
        
        nome_arquivo_servidor = f"{uuid.uuid4()}.{extensao}"
        caminho_completo = os.path.join(UPLOAD_DIRECTORY, nome_arquivo_servidor)
        
        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True) # Garante que o diretório exista
        
        with open(caminho_completo, "wb") as buffer:
            buffer.write(image_bytes)
        logger.info(f"TASK INFO: Arquivo salvo no servidor em {caminho_completo}")
        
        # 4. Registrar a foto no banco de dados
        url_acesso_foto = f"/fotos-promotores/{nome_arquivo_servidor}"
        crud_foto.create_foto_registro(
            db=db,
            url_foto=url_acesso_foto,
            nome_arquivo=nome_arquivo_servidor,
            legenda=caption,
            promotor_id=promotor.id,
            empresa_id=promotor.empresa_id
        )

        logger.info(f"TASK SUCESSO: Foto de {promotor.nome} ({from_number}) foi registrada no banco de dados com sucesso.")

    except httpx.HTTPStatusError as e:
        logger.error(f"TASK ERRO: Falha ao baixar mídia da Twilio. Status: {e.response.status_code}. Resposta: {e.response.text}")
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