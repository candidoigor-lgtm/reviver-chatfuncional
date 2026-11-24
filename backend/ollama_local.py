
"""Integração do ReViver com Ollama local."""

import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=True)


def explicar(pergunta, resultado):
    modelo = os.getenv("OLLAMA_MODELO", "qwen3.5:4b").strip()

    if not modelo:
        raise RuntimeError("Configure OLLAMA_MODELO no arquivo .env.")

    instrucoes = (
        "Explique os dados do projeto acadêmico ReViver "
        "em português brasileiro, em até duas frases. "
        "Use somente os números recebidos. "
        "Não invente dados, não tire conclusões clínicas "
        "e não afirme que os dados representam pessoas reais. "
        "Os dados podem ser fictícios."
    )

    dados = {
        "pergunta": pergunta,
        "resultado": resultado
    }

    corpo = {
    "model": modelo,
    "stream": False,
    "think": False,
    "options": {
        "temperature": 0,
        "num_predict": 160
    },
        "messages": [
            {
                "role": "system",
                "content": instrucoes
            },
            {
                "role": "user",
                "content": json.dumps(dados, ensure_ascii=False)
            }
        ]
    }

    url = os.getenv(
        "OLLAMA_BASE_URL",
        "http://127.0.0.1:11434/api/chat"
    ).strip()

    pedido = Request(
        url,
        data=json.dumps(corpo).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urlopen(pedido, timeout=90) as resposta:
            retorno = json.load(resposta)

        texto = retorno.get("message", {}).get("content", "")

        if not isinstance(texto, str) or not texto.strip():
            raise ValueError("O modelo não devolveu uma explicação.")

        return texto.strip()

    except HTTPError as erro:
        detalhe = erro.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(
            f"Erro HTTP {erro.code} no Ollama local: {detalhe}"
        ) from erro

    except URLError as erro:
        raise RuntimeError(
            "Não foi possível conectar ao Ollama local. "
            "Verifique se o serviço está funcionando."
        ) from erro

    except (ValueError, KeyError, TypeError) as erro:
        raise RuntimeError(
            f"Erro ao interpretar a resposta do Ollama: {erro}"
        ) from erro
