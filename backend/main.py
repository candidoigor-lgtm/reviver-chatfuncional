
"""Ponto de entrada da API ReViver."""

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Carrega as configurações do projeto
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env", override=True)


# Importação das rotas
from backend.routes import catalogo, dashboard, health, resumo, chat
from backend.controller.chat import router as chat_dados_router


app = FastAPI(
    title="API ReViver — Ciência de Dados",
    description=(
        "API de catálogo educativo, clínicas e indicadores demonstrativos."
    ),
    version="1.0.0",
)


# Permite a comunicação entre frontend e backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:5501",
        "http://localhost:5501",
        "http://0.0.0.0:5500",
        "http://0.0.0.0:5501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Impede o navegador de armazenar respostas da API em cache
@app.middleware("http")
async def impedir_cache_dos_dados(request, call_next):
    response = await call_next(request)

    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response


# Registra as rotas da API
app.include_router(health.router)
app.include_router(catalogo.router)
app.include_router(resumo.router)
app.include_router(dashboard.router)

# Chatbot de conversação
app.include_router(chat.router)

# Chat de consultas dos dados
app.include_router(chat_dados_router)


@app.get("/", tags=["Início"])
def inicio():
    return {
        "projeto": "ReViver",
        "status": "online",
        "docs": "/docs",
        "health": "/api/health",
    }
