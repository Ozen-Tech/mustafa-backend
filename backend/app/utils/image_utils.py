from urllib.parse import urlparse, parse_qs
from app.core.config import settings

def convert_twilio_url_to_proxy(twilio_url: str, base_url: str = None) -> str:
    """
    Converte uma URL do Twilio em uma URL do proxy local.
    
    Args:
        twilio_url: URL original do Twilio (ex: https://api.twilio.com/2010-04-01/Accounts/...)
        base_url: URL base do backend (opcional, usa settings se não fornecido)
    
    Returns:
        URL do proxy (ex: https://backend.com/proxy/image-proxy?url=...)
    """
    if not twilio_url or "api.twilio.com" not in twilio_url:
        return twilio_url
    
    # Usar URL base das configurações se não fornecida
    if not base_url:
        base_url = getattr(settings, 'BACKEND_URL', 'https://mustafa-backend-6ywg.onrender.com')
    
    # Remover barra final se existir
    base_url = base_url.rstrip('/')
    
    # Criar URL do proxy
    proxy_url = f"{base_url}/proxy/image-proxy?url={twilio_url}"
    
    return proxy_url

def extract_twilio_ids_from_url(twilio_url: str) -> dict:
    """
    Extrai os IDs (account_sid, message_sid, media_sid) de uma URL do Twilio.
    
    Args:
        twilio_url: URL do Twilio
    
    Returns:
        Dict com os IDs extraídos ou None se não for uma URL válida do Twilio
    """
    if not twilio_url or "api.twilio.com" not in twilio_url:
        return None
    
    try:
        # Exemplo: https://api.twilio.com/2010-04-01/Accounts/AC.../Messages/MM.../Media/ME...
        parts = twilio_url.split('/')
        
        # Encontrar os índices dos componentes
        accounts_idx = None
        messages_idx = None
        media_idx = None
        
        for i, part in enumerate(parts):
            if part == 'Accounts' and i + 1 < len(parts):
                accounts_idx = i + 1
            elif part == 'Messages' and i + 1 < len(parts):
                messages_idx = i + 1
            elif part == 'Media' and i + 1 < len(parts):
                media_idx = i + 1
        
        if accounts_idx and messages_idx and media_idx:
            return {
                'account_sid': parts[accounts_idx],
                'message_sid': parts[messages_idx],
                'media_sid': parts[media_idx]
            }
    
    except (IndexError, AttributeError):
        pass
    
    return None

def is_twilio_url(url: str) -> bool:
    """
    Verifica se uma URL é do Twilio.
    
    Args:
        url: URL para verificar
    
    Returns:
        True se for uma URL do Twilio, False caso contrário
    """
    return url and "api.twilio.com" in url

def is_placeholder_url(url: str) -> bool:
    """
    Verifica se uma URL é um placeholder.
    
    Args:
        url: URL para verificar
    
    Returns:
        True se for um placeholder, False caso contrário
    """
    if not url:
        return True
    
    placeholder_indicators = [
        "placeholder",
        "via.placeholder.com",
        "demo",
        "sample",
        "Foto+Indisponivel"
    ]
    
    return any(indicator in url for indicator in placeholder_indicators)