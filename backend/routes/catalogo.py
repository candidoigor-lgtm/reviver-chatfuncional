from fastapi import APIRouter, HTTPException
from backend.services.csv_service import records
router = APIRouter(prefix="/api", tags=["Catálogo"])

@router.get("/substancias")
def substancias():
    try:
        return records("substancias")
    except (OSError, ValueError, UnicodeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

@router.get("/clinicas")
def clinicas():
    try:
        return {"itens": records("clinicas"), "dados_demonstrativos": True}
    except (OSError, ValueError, UnicodeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
