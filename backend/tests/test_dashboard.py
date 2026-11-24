from backend.services.analise_dashboard import conversas_por_dia, encaminhamentos_por_dia


def test_totais_diarios_reconciliam_com_csv():
    conversas = conversas_por_dia()
    encaminhamentos = encaminhamentos_por_dia()
    assert sum(item["total_conversas"] for item in conversas) == 300
    assert sum(item["total_encaminhamentos"] for item in encaminhamentos) == 88
    assert [item["data"] for item in conversas] == sorted(item["data"] for item in conversas)
