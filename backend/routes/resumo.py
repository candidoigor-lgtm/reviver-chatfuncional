from fastapi import APIRouter, HTTPException
from backend.services.analise_service import indicadores, resumo_por_substancia
from backend.services.csv_service import read_csv
router = APIRouter(prefix="/api/resumo", tags=["Ciência de Dados"])

@router.get("/indicadores")
def get_indicadores():
    try:
        return indicadores()
    except (OSError, ValueError, UnicodeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

@router.get("/substancias")
def get_resumo_substancias():
    try:
        return resumo_por_substancia()
    except (OSError, ValueError, UnicodeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

@router.get("/csv")
def csv_info():
    try:
        df = read_csv("resultados")
        return {"arquivo": "ReViver_resultados_por_substancia_900_LINHAS_DADOS_FICTICIOS.csv", "linhas": int(len(df)), "colunas": list(df.columns), "dados_ficticios": True}
    except (OSError, ValueError, UnicodeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
