
"""Chatbot ReViver com integração ao Ollama local."""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env", override=True)

OLLAMA_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434/api/chat"
).strip()

router = APIRouter(
    prefix="/api/chat/mensagem",
    tags=["Chatbot"]
)


class MensagemChat(BaseModel):
    mensagem: str = Field(min_length=1, max_length=2000)


def resposta_local(mensagem: str) -> str:
    """Respostas automáticas caso o Ollama não esteja disponível."""

    t = mensagem.casefold()

    if any(x in t for x in [
        "urgente", "socorro", "overdose",
        "não consigo respirar", "desmaiei",
        "convuls", "perigo agora"
    ]):
        return (
            "Isso pode ser uma emergência. Ligue para o SAMU (192) "
            "ou procure uma UPA/pronto-socorro agora. "
            "Se possível, peça a uma pessoa adulta de confiança "
            "para ficar com você. Não espere pelo chatbot."
        )

    if any(x in t for x in [
        "cocaína", "cocaina", "crack",
        "heroína", "heroina", "maconha",
        "álcool", "alcool", "droga",
        "substância", "substancia"
    ]):
        return (
            "Obrigado por falar sobre isso. O uso de substâncias "
            "pode afetar a saúde de formas diferentes. Converse "
            "com um profissional de saúde ou procure uma UBS ou CAPS AD."
        )

    if any(x in t for x in [
        "família", "familia", "meu filho",
        "minha mãe", "meu pai", "amigo"
    ]):
        return (
            "Apoiar alguém começa com uma conversa calma, sem "
            "acusações. Escute, demonstre preocupação e incentive "
            "a pessoa a procurar uma UBS ou CAPS AD com apoio "
            "profissional. Familiares também podem buscar orientação."
        )

    if any(x in t for x in [
        "ajuda", "parar", "deixar", "viciado",
        "dependência", "dependencia"
    ]):
        return (
            "Você não precisa resolver tudo de uma vez nem passar "
            "por isso sozinho. Um profissional pode ajudar a construir "
            "um plano adequado à sua situação. Procure uma UBS ou "
            "CAPS AD e converse com um adulto de confiança."
        )

    if any(x in t for x in [
        "oi", "olá", "ola", "bom dia",
        "boa tarde", "boa noite"
    ]):
        return (
            "Olá! Você pode me contar o que gostaria de entender "
            "ou qual tipo de apoio procura. Vou responder com respeito "
            "e sem julgamentos."
        )

    return (
        "Quero compreender melhor para não presumir o que você está "
        "vivendo. Você procura informações sobre substâncias, apoio "
        "para você, orientação para alguém da família ou ajuda para "
        "encontrar um serviço de saúde?"
    )


@router.post("")
async def conversar(dados: MensagemChat):

    mensagem = dados.mensagem.strip()

    if not mensagem:
        return {
            "resposta": "Digite uma mensagem para iniciar a conversa.",
            "ia_ativa": False,
            "aviso": ""
        }

    modelo = (
        os.getenv("OLLAMA_MODELO", "").strip()
        or os.getenv("OLLAMA_MODEL", "").strip()
        or "qwen3.5:4b"
    )

    fallback = resposta_local(mensagem)

    # Carrega uma parte do catálogo educativo
    arquivo_csv = ROOT / "substancias.csv"

    try:
        contexto = "\n".join(
            arquivo_csv.read_text(
                encoding="utf-8-sig"
            ).splitlines()[:20]
        )
    except OSError:
        contexto = "Catálogo educativo indisponível."

    # Instruções do chatbot
    system = (
        "Você é o assistente educativo do projeto ReViver. "
        "O ReViver é uma plataforma de apoio a pessoas que "
        "enfrentam problemas relacionados ao uso de substâncias "
        "e também aos seus familiares. "
        "O projeto oferece orientações, informações educativas "
        "sobre substâncias, apoio aos familiares e ajuda para "
        "encontrar serviços de saúde. "
        "Seu objetivo é acolher, orientar e incentivar a busca "
        "por ajuda profissional, sem julgamentos. "
        "Responda em português brasileiro, com clareza e de "
        "forma direta. "
        "Não invente funcionalidades, clínicas ou informações. "
        "Não diagnostique, prescreva tratamentos ou prometa resultados. "
        "O ReViver é complementar e não substitui profissionais "
        "de saúde. "
        "Incentive a procura por UBS ou CAPS AD. "
        "Em emergências, oriente a procurar uma UPA ou ligar "
        "para o SAMU (192), com apoio de um adulto de confiança. "
        "Não solicite dados pessoais. "
        "Use o catálogo educativo abaixo somente quando for relevante:\n"
        + contexto
    )

    try:
        async with httpx.AsyncClient(timeout=240) as client:

            resposta = await client.post(
                OLLAMA_URL,
                json={
                    "model": modelo,
                    "stream": False,
                    "think": False,
                    "options": {
                        "num_gpu": 0,
                        "num_ctx": 2048,
                        "num_predict": -1,
                        "temperature": 0
                    },
                    "messages": [
                        {
                            "role": "system",
                            "content": system
                        },
                        {
                            "role": "user",
                            "content": mensagem
                        }
                    ]
                }
            )

            resposta.raise_for_status()
            resultado = resposta.json()

            answer = (
                resultado
                .get("message", {})
                .get("content", "")
            )

            if not isinstance(answer, str) or not answer.strip():
                raise ValueError(
                    "O Ollama retornou uma resposta vazia."
                )

        return {
            "resposta": answer.strip(),
            "ia_ativa": True,
            "aviso": ""
        }

    except httpx.HTTPStatusError as erro:
        return {
            "resposta": fallback,
            "ia_ativa": False,
            "aviso": (
                f"Erro HTTP {erro.response.status_code}: "
                f"{erro.response.text[:300]}"
            )
        }

    except httpx.RequestError as erro:
        return {
            "resposta": fallback,
            "ia_ativa": False,
            "aviso": (
                f"Erro de conexão com Ollama local: {str(erro)[:200]}"
            )
        }

    except (ValueError, KeyError, TypeError, AttributeError) as erro:
        return {
            "resposta": fallback,
            "ia_ativa": False,
            "aviso": f"Erro na resposta do Ollama: {str(erro)}"
        }
