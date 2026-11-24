
"""Consultas que o chatbot pode responder usando os CSVs do ReViver."""

from backend.services.csv_service import read_csv


AVISO_DADOS = (
    "Os arquivos usados nesta demonstração contêm dados fictícios. "
    "Os números não representam pacientes reais nem eficácia clínica."
)


def _contar(df, coluna, valor=None):
    """Conta registros preenchidos ou que correspondem a um valor."""

    if coluna not in df.columns:
        return 0

    serie = df[coluna].fillna("").astype(str).str.strip()

    if valor is None:
        return int(serie.ne("").sum())

    return int(
        serie.str.casefold().eq(valor.casefold()).sum()
    )


def totalizar_usuarios():
    dados = read_csv("usuarios")

    total = (
        int(dados["id_usuario"].nunique())
        if "id_usuario" in dados.columns
        else len(dados)
    )

    return {
        "total_usuarios": total,
        "familiares": _contar(dados, "tipo_usuario", "familiar"),
        "pessoas_interessadas": _contar(
            dados, "tipo_usuario", "interessado"
        ),
        "pessoas_em_acompanhamento": _contar(
            dados, "tipo_usuario", "pessoa_em_acompanhamento"
        ),
        "dados_ficticios": True,
    }


def totalizar_conversas():
    dados = read_csv("conversas")

    total = (
        int(dados["id_conversa"].nunique())
        if "id_conversa" in dados.columns
        else len(dados)
    )

    return {
        "total_conversas": total,
        "necessitam_profissional": _contar(
            dados, "necessita_profissional", "sim"
        ),
        "com_nivel_atencao": _contar(
            dados, "nivel_de_urgencia", "atencao"
        ),
        "encaminhamentos_realizados": _contar(
            dados, "encaminhamento_realizado", "sim"
        ),
        "dados_ficticios": True,
    }


def totalizar_clinicas():
    dados = read_csv("clinicas")

    return {
        "total_registros_clinicas": len(dados),
        "ativas": _contar(dados, "status_atendimento", "ativo"),
        "aguardando_confirmacao": _contar(
            dados, "status_atendimento", "aguardando_confirmacao"
        ),
        "encerradas": _contar(
            dados, "status_atendimento", "encerrado"
        ),
        "dados_ficticios": True,
    }


def totalizar_substancias():
    dados = read_csv("substancias")

    if "substancia" in dados.columns:
        serie = (
            dados["substancia"]
            .dropna()
            .astype(str)
            .str.strip()
        )
        total = int(serie[serie.ne("")].nunique())
    else:
        total = len(dados)

    return {
        "total_substancias_catalogadas": total,
        "dados_ficticios": False,
    }


def totalizar_resultados():
    dados = read_csv("resultados")

    coluna = "meta_acompanhamento_atingida"

    if coluna in dados.columns:
        status = (
            dados[coluna]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.casefold()
        )

        metas_atingidas = int(status.eq("sim").sum())
        metas_parciais = int(status.eq("parcialmente").sum())
        metas_nao_atingidas = int(
            status.isin(["não", "nao"]).sum()
        )
    else:
        metas_atingidas = 0
        metas_parciais = 0
        metas_nao_atingidas = 0

    return {
        "total_registros": len(dados),
        "metas_atingidas": metas_atingidas,
        "metas_parciais": metas_parciais,
        "metas_nao_atingidas": metas_nao_atingidas,
        "dados_ficticios": True,
    }


# Perguntas disponíveis para o chatbot
CONSULTAS = {
    "Quantos usuários estão registrados?": totalizar_usuarios,
    "Quantas conversas existem no CSV?": totalizar_conversas,
    "Quantos encaminhamentos profissionais foram registrados?": totalizar_conversas,
    "Quantas clínicas aparecem no CSV e quais são seus status?": totalizar_clinicas,
    "Quantas substâncias existem no catálogo?": totalizar_substancias,
    "Quantos registros de acompanhamento existem?": totalizar_resultados,
}


def encontrar_pergunta(texto):
    """Identifica se a pergunta existe na lista cadastrada."""

    texto = texto.strip().casefold()

    for pergunta in CONSULTAS:
        if pergunta.casefold() == texto:
            return pergunta

    return None


def consultar(pergunta):
    """Executa a consulta correspondente à pergunta."""

    if pergunta not in CONSULTAS:
        raise ValueError("Pergunta não cadastrada.")

    resultado = CONSULTAS[pergunta]()

    # Retorna somente o indicador solicitado.
    if pergunta == (
        "Quantos encaminhamentos profissionais foram registrados?"
    ):
        return {
            "encaminhamentos_realizados": (
                resultado["encaminhamentos_realizados"]
            ),
            "dados_ficticios": True,
        }

    return resultado
