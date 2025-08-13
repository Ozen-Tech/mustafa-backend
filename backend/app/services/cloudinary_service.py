import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class CloudinaryService:
    def __init__(self):
        # Configurar Cloudinary com variáveis de ambiente
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
            secure=True
        )
    
    def upload_image(self, image_bytes: bytes, filename: str, folder: str = "fotos-promotores") -> Optional[dict]:
        """
        Faz upload de uma imagem para o Cloudinary
        
        Args:
            image_bytes: Bytes da imagem
            filename: Nome do arquivo (será usado como public_id)
            folder: Pasta no Cloudinary onde salvar
            
        Returns:
            Dict com informações do upload ou None se falhar
        """
        try:
            # Remove a extensão do filename para usar como public_id
            public_id = os.path.splitext(filename)[0]
            
            result = cloudinary.uploader.upload(
                image_bytes,
                public_id=public_id,
                folder=folder,
                resource_type="image",
                format="jpg",  # Força conversão para JPG para padronizar
                quality="auto",  # Otimização automática
                fetch_format="auto"  # Formato automático baseado no browser
            )
            
            logger.info(f"Upload realizado com sucesso: {result['public_id']}")
            return result
            
        except Exception as e:
            logger.error(f"Erro no upload para Cloudinary: {str(e)}")
            return None
    
    def delete_image(self, public_id: str) -> bool:
        """
        Deleta uma imagem do Cloudinary
        
        Args:
            public_id: ID público da imagem no Cloudinary
            
        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get('result') == 'ok'
        except Exception as e:
            logger.error(f"Erro ao deletar imagem do Cloudinary: {str(e)}")
            return False
    
    def get_optimized_url(self, public_id: str, width: int = 800, height: int = 600) -> str:
        """
        Gera uma URL otimizada da imagem
        
        Args:
            public_id: ID público da imagem
            width: Largura desejada
            height: Altura desejada
            
        Returns:
            URL otimizada da imagem
        """
        url, _ = cloudinary_url(
            public_id,
            width=width,
            height=height,
            crop="fill",
            quality="auto",
            fetch_format="auto"
        )
        return url

# Instância global do serviço
cloudinary_service = CloudinaryService()