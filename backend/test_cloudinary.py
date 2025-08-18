#!/usr/bin/env python3
"""
Script para testar a configuração do Cloudinary
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.cloudinary_service import cloudinary_service

def test_cloudinary():
    print("=== TESTE DO CLOUDINARY ===")
    print("1. Testando configuração...")
    
    try:
        # Teste de upload com uma imagem de placeholder
        test_url = "https://via.placeholder.com/300x200.png"
        result = cloudinary_service.upload_image(test_url, "teste_config")
        
        print("✅ Upload bem-sucedido!")
        print(f"URL gerada: {result['secure_url']}")
        print(f"Public ID: {result['public_id']}")
        
        # Teste de exclusão
        print("\n2. Testando exclusão...")
        delete_result = cloudinary_service.delete_image(result['public_id'])
        print(f"✅ Exclusão bem-sucedida: {delete_result['result']}")
        
        print("\n🎉 CLOUDINARY FUNCIONANDO PERFEITAMENTE!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Configure as mesmas variáveis no painel do Render")
        print("2. Faça o redeploy do serviço")
        print("3. As novas fotos serão salvas corretamente no Cloudinary")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        print("\n🔧 SOLUÇÕES:")
        print("1. Verifique se as variáveis de ambiente estão corretas no .env")
        print("2. Certifique-se de que as credenciais do Cloudinary são válidas")
        print("3. Verifique sua conexão com a internet")
        
        return False

if __name__ == "__main__":
    test_cloudinary()