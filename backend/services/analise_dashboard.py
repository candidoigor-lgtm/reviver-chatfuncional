"""Análises diárias das conversas e dos encaminhamentos do ReViver."""
import pandas as pd

from backend.services.csv_service import read_csv

AVISO_DADOS = (
    "Dados fictícios para demonstração. Não representam pessoas reais, "
    "atendimentos reais ou eficácia de tratamento."
)


def carregar_conversas_dashboard() -> pd.DataFrame:
    dados = read_csv("conversas")
    obrigatorias = {"id_conversa", "data_hora", "encaminhamento_realizado"}
    faltantes = obrigatorias - set(dados.columns)
    if faltantes:
        raise ValueError("Colunas ausentes em conversas.csv: " + ", ".join(sorted(faltantes)))
    if dados.empty:
        dados["data"] = pd.Series(dtype="string")
        return dados

    if dados["id_conversa"].isna().any() or dados["id_conversa"].str.strip().eq("").any():
        raise ValueError("Há conversa sem id_conversa.")
    if dados["id_conversa"].duplicated().any():
        raise ValueError("Há id_conversa duplicado em conversas.csv.")

    datas = pd.to_datetime(dados["data_hora"], errors="coerce")
    if datas.isna().any():
        raise ValueError("data_hora contém data ou horário inválido.")
    dados["data"] = datas.dt.strftime("%Y-%m-%d")

    status = dados["encaminhamento_realizado"].str.strip().str.casefold()
    validos = {"sim", "nao", "não"}
    if not status.isin(validos).all():
        raise ValueError("encaminhamento_realizado deve conter sim ou nao.")
    dados["encaminhamento_realizado"] = status.isin({"sim"})
    return dados


def conversas_por_dia() -> list[dict]:
    """Conta conversas distintas registradas em cada dia."""
    dados = carregar_conversas_dashboard()
    if dados.empty:
        return []
    totais = dados.groupby("data")["id_conversa"].nunique().sort_index()
    return [
        {"data": data, "total_conversas": int(total)}
        for data, total in totais.items()
    ]


def encaminhamentos_por_dia() -> list[dict]:
    """Conta conversas com encaminhamento realizado em cada dia."""
    dados = carregar_conversas_dashboard()
    if dados.empty:
        return []
    totais = (
        dados.groupby("data")["encaminhamento_realizado"]
        .sum()
        .sort_index()
    )
    return [
        {"data": data, "total_encaminhamentos": int(total)}
        for data, total in totais.items()
    ]


def indicadores_gerais() -> dict:
    """Indicadores descritivos calculados diretamente dos CSVs do projeto."""
    usuarios = read_csv("usuarios")
    conversas = read_csv("conversas")
    clinicas = read_csv("clinicas")

    def contar(df, coluna, valor):
        if coluna not in df.columns:
            return 0
        return int(df[coluna].fillna("").astype(str).str.strip().str.casefold().eq(valor).sum())

    total_usuarios, total_conversas, total_clinicas = len(usuarios), len(conversas), len(clinicas)
    encaminhadas = contar(conversas, "encaminhamento_realizado", "sim")
    precisam_profissional = contar(conversas, "necessita_profissional", "sim")
    com_atencao = contar(conversas, "nivel_de_urgencia", "atencao")
    consentimentos = contar(usuarios, "consentimento_dados", "sim")
    clinicas_ativas = contar(clinicas, "status_atendimento", "ativo")
    aguardando = contar(clinicas, "status_atendimento", "aguardando_confirmacao")
    encerradas = contar(clinicas, "status_atendimento", "encerrado")
    pct = lambda n, total: round(n * 100 / total, 1) if total else 0
    return {
        "dados_ficticios": True,
        "aviso": "Dados fictícios para demonstração acadêmica. Não representam pessoas reais, atendimentos reais nem eficácia de tratamento.",
        "usuarios": {"total": int(total_usuarios), "interessados": contar(usuarios, "tipo_usuario", "interessado"), "familiares": contar(usuarios, "tipo_usuario", "familiar"), "em_acompanhamento": contar(usuarios, "tipo_usuario", "pessoa_em_acompanhamento"), "consentimento_confirmado": consentimentos, "taxa_consentimento": pct(consentimentos, total_usuarios)},
        "conversas": {"total": int(total_conversas), "precisam_profissional": precisam_profissional, "percentual_precisam_profissional": pct(precisam_profissional, total_conversas), "com_atencao": com_atencao, "percentual_com_atencao": pct(com_atencao, total_conversas), "encaminhamentos_realizados": encaminhadas, "encaminhamentos_nao_realizados": int(total_conversas - encaminhadas), "taxa_encaminhamento": pct(encaminhadas, total_conversas)},
        "clinicas": {"total": int(total_clinicas), "ativas": clinicas_ativas, "aguardando_confirmacao": aguardando, "encerradas": encerradas, "taxa_ativas": pct(clinicas_ativas, total_clinicas)}
    }
