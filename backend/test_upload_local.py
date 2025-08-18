import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import tempfile
from PIL import Image

# Carrega variáveis do .env
load_dotenv(dotenv_path='../.env')

print("=== TESTE DE UPLOAD LOCAL CLOUDINARY ===")

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
    # Cria uma imagem simples localmente
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        # Cria uma imagem 100x100 vermelha
        img = Image.new('RGB', (100, 100), color='red')
        img.save(tmp_file.name, 'PNG')
        
        print(f"1. Criada imagem temporária: {tmp_file.name}")
        
        # Testa upload
        print("2. Fazendo upload para Cloudinary...")
        result = cloudinary.uploader.upload(
            tmp_file.name,
            public_id="teste_local_" + str(int(os.time.time())),
            resource_type="image"
        )
        
        print("✅ UPLOAD BEM-SUCEDIDO!")
        print(f"URL da imagem: {result['secure_url']}")
        print(f"Public ID: {result['public_id']}")
        print(f"Formato: {result['format']}")
        print(f"Tamanho: {result['bytes']} bytes")
        
        # Remove arquivo temporário
        os.unlink(tmp_file.name)
        print("\n🎉 CLOUDINARY ESTÁ FUNCIONANDO PERFEITAMENTE!")
        
except Exception as e:
    print(f"❌ ERRO NO UPLOAD: {str(e)}")
    print("\n🔧 Verifique:")
    print("1. Conexão com a internet")
    print("2. Credenciais do Cloudinary")
    print("3. Permissões da conta Cloudinary")