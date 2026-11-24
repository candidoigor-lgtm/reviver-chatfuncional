
"""Rotas do chat de consultas do ReViver."""

from urllib.error import HTTPError, URLError

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.chat_dados import (
    AVISO_DADOS,
    CONSULTAS,
    consultar,
    encontrar_pergunta,
)

from backend.ollama_local import explicar


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat de dados"]
)


class EntradaChat(BaseModel):
    pergunta: str = Field(min_length=1, max_length=300)


@router.get("/perguntas")
def listar_perguntas():
    """Retorna as perguntas disponíveis para consulta."""
    return list(CONSULTAS)


@router.post("")
def responder_consulta(entrada: EntradaChat):
    """Consulta os dados e utiliza o Ollama local para explicar."""

    pergunta = encontrar_pergunta(entrada.pergunta)

    if pergunta is None:
        return {
            "resultado": None,
            "explicacao": None,
            "aviso": "Escolha uma pergunta disponível na lista.",
            "dados_ficticios": True,
        }

    # O Python consulta os CSVs antes de chamar a inteligência artificial.
    resultado = consultar(pergunta)

    explicacao = None
    aviso = None

    try:
        # O Ollama local apenas explica o resultado calculado pelo Python.
        explicacao = explicar(pergunta, resultado)

    except RuntimeError as erro:
        aviso = str(erro)

    except HTTPError as erro:
        aviso = (
            f"O Ollama local retornou HTTP {erro.code}. "
            "O cálculo dos dados continua disponível."
        )

    except (URLError, OSError, ValueError, KeyError, TypeError):
        aviso = (
            "Não foi possível obter a explicação do Ollama local. "
            "O cálculo dos dados continua disponível."
        )

    return {
        "pergunta": pergunta,
        "resultado": resultado,
        "explicacao": explicacao,
        "aviso": aviso,
        "dados_ficticios": resultado.get("dados_ficticios", True),
        "aviso_dados": (
            AVISO_DADOS
            if resultado.get("dados_ficticios", True)
            else ""
        ),
    }
