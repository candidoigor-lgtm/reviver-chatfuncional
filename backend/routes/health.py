from fastapi import APIRouter
router = APIRouter(tags=["Estado da API"])

@router.get("/api/health")
def health():
    return {"status": "online", "projeto": "ReViver", "servico": "API de dados"}
