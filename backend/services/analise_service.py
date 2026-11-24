"""Indicadores descritivos dos registros demonstrativos do ReViver."""
from .csv_service import read_csv

AVISO = "Dados fictícios para demonstração; não representam pacientes reais nem eficácia clínica."


def indicadores() -> dict:
    df = read_csv("resultados")
    substance_col = next((c for c in df.columns if c.strip().lower() in {"substancia_registrada", "substância registrada", "substancia", "substância"}), None)
    status_col = next((c for c in df.columns if c.strip().lower() in {"meta_acompanhamento_atingida", "meta acompanhamento atingida"}), None)
    statuses = df[status_col].fillna("").str.strip().str.casefold() if status_col else []
    atingidas = int((statuses == "sim").sum()) if status_col else 0
    parciais = int((statuses == "parcialmente").sum()) if status_col else 0
    nao = int(statuses.isin(["não", "nao"]).sum()) if status_col else 0
    total = len(df)
    return {
        "dados_ficticios": True,
        "aviso": AVISO,
        "total_registros": int(total),
        "total_substancias": int(df[substance_col].dropna().nunique()) if substance_col else 0,
        "metas_atingidas": atingidas,
        "metas_parciais": parciais,
        "metas_nao_atingidas": nao,
        "percentual_meta_atingida": round(atingidas * 100 / total, 1) if total else 0,
    }


def resumo_por_substancia() -> dict:
    df = read_csv("resultados")
    substance_col = next((c for c in df.columns if c.strip().lower() in {"substancia_registrada", "substância registrada", "substancia", "substância"}), None)
    status_col = next((c for c in df.columns if c.strip().lower() in {"meta_acompanhamento_atingida", "meta acompanhamento atingida"}), None)
    if not substance_col:
        return {"dados_ficticios": True, "aviso": AVISO, "itens": [], "erro": "Coluna de substância não encontrada."}
    grouped = {}
    for _, row in df.iterrows():
        name = str(row.get(substance_col) or "Não informado")
        item = grouped.setdefault(name, {"substancia_registrada": name, "registros": 0, "metas_atingidas": 0, "metas_parciais": 0, "metas_nao_atingidas": 0})
        item["registros"] += 1
        status = str(row.get(status_col) or "").strip().casefold() if status_col else ""
        if status == "sim": item["metas_atingidas"] += 1
        elif status == "parcialmente": item["metas_parciais"] += 1
        elif status in {"não", "nao"}: item["metas_nao_atingidas"] += 1
    return {"dados_ficticios": True, "aviso": AVISO, "itens": sorted(grouped.values(), key=lambda x: x["registros"], reverse=True)}
