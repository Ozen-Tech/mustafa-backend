import os
import time
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv(dotenv_path='../.env')

print("=== TESTE DE UPLOAD SIMPLES CLOUDINARY ===")

# Configura Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

print(f"Cloud Name: {os.getenv('CLOUDINARY_CLOUD_NAME')}")
print(f"API Key: {os.getenv('CLOUDINARY_API_KEY')}")
print()

try:
    # Testa upload de um arquivo de texto simples
    print("1. Fazendo upload de arquivo de texto para Cloudinary...")
    result = cloudinary.uploader.upload(
        "test_image.txt",
        public_id="teste_texto_" + str(int(time.time())),
        resource_type="raw"  # Para arquivos não-imagem
    )
    
    print("✅ UPLOAD BEM-SUCEDIDO!")
    print(f"URL do arquivo: {result['secure_url']}")
    print(f"Public ID: {result['public_id']}")
    if 'format' in result:
        print(f"Formato: {result['format']}")
    if 'bytes' in result:
        print(f"Tamanho: {result['bytes']} bytes")
    
    print("\n🎉 CLOUDINARY ESTÁ FUNCIONANDO PERFEITAMENTE!")
    print("✅ O sistema de upload está operacional!")
    
except Exception as e:
    print(f"❌ ERRO NO UPLOAD: {str(e)}")
    print("\n🔧 Verifique:")
    print("1. Conexão com a internet")
    print("2. Credenciais do Cloudinary")
    print("3. Permissões da conta Cloudinary")