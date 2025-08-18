import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv(dotenv_path='../.env')

print("=== DEBUG CLOUDINARY CREDENTIALS ===")
print(f"Cloud Name: {os.getenv('CLOUDINARY_CLOUD_NAME')}")
print(f"API Key: {os.getenv('CLOUDINARY_API_KEY')}")
print(f"API Secret: {os.getenv('CLOUDINARY_API_SECRET')[:5]}...")
print()

# Teste com diferentes combinações baseadas nas imagens
credentials_to_test = [
    {
        'cloud_name': 'duk91uunh',
        'api_key': '975393196452262',
        'api_secret': 'nwRSGOKJFJc'
    },
    {
        'cloud_name': 'duk91uunh', 
        'api_key': '975393196452262',
        'api_secret': 'giD7jfW0VJ2LCE3UsW_BG3BP8_s'
    },
    {
        'cloud_name': 'duk91uunh',
        'api_key': '822349327384637',
        'api_secret': 'nwRSGOKJFJc'
    }
]

for i, creds in enumerate(credentials_to_test, 1):
    print(f"\n--- TESTE {i} ---")
    print(f"Cloud Name: {creds['cloud_name']}")
    print(f"API Key: {creds['api_key']}")
    print(f"API Secret: {creds['api_secret'][:5]}...")
    
    try:
        # Configura Cloudinary
        cloudinary.config(
            cloud_name=creds['cloud_name'],
            api_key=creds['api_key'],
            api_secret=creds['api_secret']
        )
        
        # Testa listagem de recursos
        result = cloudinary.api.resources(max_results=1)
        print("✅ SUCESSO! Credenciais funcionam.")
        print(f"Total de recursos: {result.get('total_count', 0)}")
        break
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        continue
else:
    print("\n❌ NENHUMA COMBINAÇÃO DE CREDENCIAIS FUNCIONOU")
    print("\n🔧 PRÓXIMOS PASSOS:")
    print("1. Verifique se a conta Cloudinary está ativa")
    print("2. Gere novas API Keys no painel do Cloudinary")
    print("3. Verifique se não há restrições de IP")