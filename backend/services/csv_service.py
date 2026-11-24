
"""Leitura centralizada e segura dos CSVs usados pela API ReViver."""

from pathlib import Path

import pandas as pd


# Caminho principal do projeto
PROJECT_ROOT = Path(__file__).resolve().parents[2]


# Arquivos CSV utilizados pelo sistema
CSV_FILES = {
    "usuarios": PROJECT_ROOT / "usuarios.csv",
    "substancias": PROJECT_ROOT / "substancias.csv",
    "clinicas": PROJECT_ROOT / "clinicas.csv",
    "conversas": PROJECT_ROOT / "conversas.csv",
    "resultados": (
        PROJECT_ROOT
        / "ReViver_resultados_por_substancia_900_LINHAS_DADOS_FICTICIOS.csv"
    ),
}


def read_csv(source: str) -> pd.DataFrame:
    """Lê um CSV permitido e retorna seus dados em um DataFrame."""

    path = CSV_FILES.get(source)

    if path is None:
        raise ValueError(
            f"Fonte CSV não permitida: {source}"
        )

    if not path.is_file():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {path.name}"
        )

    try:
        # Detecta automaticamente vírgula ou ponto e vírgula
        df = pd.read_csv(
            path,
            sep=None,
            engine="python",
            encoding="utf-8-sig",
            dtype=str
        )

        # Limpa os nomes das colunas
        df.columns = [
            str(col).strip()
            for col in df.columns
        ]

        # Remove espaços desnecessários dos valores
        for coluna in df.columns:
            df[coluna] = df[coluna].map(
                lambda valor: (
                    valor.strip()
                    if isinstance(valor, str)
                    else valor
                )
            )

        return df

    except pd.errors.EmptyDataError:
        raise ValueError(
            f"O arquivo {path.name} está vazio."
        )

    except pd.errors.ParserError as erro:
        raise ValueError(
            f"Erro ao interpretar o CSV {path.name}: {erro}"
        ) from erro


def records(source: str) -> list[dict]:
    """Transforma os registros do CSV em uma lista de dicionários."""

    df = read_csv(source)

    # Substitui valores ausentes por None
    df = df.astype(object).where(
        pd.notna(df),
        None
    )

    return df.to_dict(orient="records")
