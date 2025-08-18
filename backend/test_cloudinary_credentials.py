#!/usr/bin/env python3
"""
Script para testar as credenciais do Cloudinary diretamente
"""

import cloudinary
import cloudinary.api
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

def test_cloudinary_credentials():
    print("=== TESTE DAS CREDENCIAIS DO CLOUDINARY ===")
    
    # Obter credenciais do .env
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    print(f"Cloud Name: {cloud_name}")
    print(f"API Key: {api_key}")
    print(f"API Secret: {'*' * len(api_secret) if api_secret else 'None'}")
    
    if not all([cloud_name, api_key, api_secret]):
        print("❌ Credenciais incompletas no arquivo .env")
        return False
    
    try:
        # Configurar Cloudinary
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        print("\n1. Testando conexão com a API...")
        
        # Testar conexão fazendo uma consulta simples
        result = cloudinary.api.ping()
        print(f"✅ Ping bem-sucedido: {result}")
        
        # Testar listagem de recursos (limitado)
        print("\n2. Testando listagem de recursos...")
        resources = cloudinary.api.resources(max_results=1)
        print(f"✅ Listagem bem-sucedida. Total de recursos: {resources.get('total_count', 0)}")
        
        print("\n🎉 CREDENCIAIS DO CLOUDINARY ESTÃO CORRETAS!")
        return True
        
    except cloudinary.exceptions.AuthorizationRequired as e:
        print(f"❌ Erro de autorização: {e}")
        print("🔧 Verifique se as credenciais estão corretas")
        return False
        
    except cloudinary.exceptions.NotFound as e:
        print(f"❌ Cloud name não encontrado: {e}")
        print("🔧 Verifique se o CLOUDINARY_CLOUD_NAME está correto")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        print(f"Tipo do erro: {type(e).__name__}")
        return False

if __name__ == "__main__":
    test_cloudinary_credentials()