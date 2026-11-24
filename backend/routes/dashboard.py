"""Rotas GET para os indicadores diários do dashboard ReViver."""
from fastapi import APIRouter, HTTPException

from backend.services.analise_dashboard import (
    AVISO_DADOS,
    conversas_por_dia,
    encaminhamentos_por_dia,
    indicadores_gerais,
)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/conversas-por-dia")
def get_conversas_por_dia():
    try:
        return {
            "dados_ficticios": True,
            "aviso": AVISO_DADOS,
            "itens": conversas_por_dia(),
        }
    except (OSError, ValueError, UnicodeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/encaminhamentos-por-dia")
def get_encaminhamentos_por_dia():
    try:
        return {
            "dados_ficticios": True,
            "aviso": AVISO_DADOS,
            "itens": encaminhamentos_por_dia(),
        }
    except (OSError, ValueError, UnicodeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/indicadores")
def get_indicadores_dashboard():
    try:
        return indicadores_gerais()
    except (OSError, ValueError, UnicodeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
