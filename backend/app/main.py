from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Nossos routers
from app.routers import auth, empresas, insights, contratos as contratos_router, webhook_whatsapp, fotos
from fastapi.staticfiles import StaticFiles

# Criação da instância principal do FastAPI
app = FastAPI(
    title="API Mustafa",
    description="API para gestão de fotos de promotores via WhatsApp.", 
    version="2.0.0"
)
VERCEL_PRODUCTION_URL = "mustafa-backend-enzoalmeida21s-projects.vercel.app"


# Configuração do CORS (já estava correta)
origins = [
    "http://localhost:3000",
    f"https://{VERCEL_PRODUCTION_URL}",
    f"https://www.{VERCEL_PRODUCTION_URL}",
    "https://mustafa-backend-k4w21ohkh-enzoalmeida21s-projects.vercel.app"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/fotos-promotores", StaticFiles(directory="uploads/fotos_promotores"), name="fotos-promotores")
app.mount("/arquivos-contratos", StaticFiles(directory="uploads"), name="arquivos-contratos")

# Incluindo todas as nossas rotas de forma limpa
# Note que no seu código, a rota de insights ainda não estava sendo incluída
# Inclusão de rotas da API
app.include_router(auth.router, prefix="/users", tags=["Usuários e Autenticação"])
app.include_router(empresas.router, prefix="/empresas", tags=["Empresas"])
app.include_router(fotos.router, prefix="/fotos", tags=["Fotos"]) # <-- prefixo /fotos para a rota ""
app.include_router(contratos_router.router, prefix="/contratos", tags=["Contratos"]) # <-- prefixo /contratos para a rota ""
app.include_router(insights.router, prefix="/insights", tags=["Insights"])

# <<<< CORREÇÃO PRINCIPAL AQUI >>>>
# Como o `webhook_whatsapp.py` JÁ TEM prefix="/webhook", nós NÃO o colocamos aqui.
app.include_router(webhook_whatsapp.router)

@app.get("/", tags=["Root"], summary="Verifica a saúde da API")
async def read_root():
    """
    Endpoint principal para verificar se a API está online.
    """
    return {"status": "ok", "message": "Bem-vindo à API da Mustafá!"}