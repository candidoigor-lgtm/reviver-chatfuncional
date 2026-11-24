# Backend ReViver (organizado)

## Organização
- `main.py`: cria a aplicação FastAPI, configura CORS e registra as rotas.
- `routes/`: endpoints HTTP divididos por responsabilidade.
- `services/csv_service.py`: leitura centralizada de CSVs permitidos.
- `services/analise_service.py`: cálculos demonstrativos para o dashboard.
- `tests/`: testes dos endpoints principais.

## Executar (Linux)
Na raiz da pasta `ReViver-main`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r backend/requirements.txt
python3 -m uvicorn backend.main:app --reload --port 8000
```

Documentação: http://127.0.0.1:8000/docs

## Rotas
- `GET /api/health`
- `GET /api/substancias`
- `GET /api/clinicas`
- `GET /api/resumo/indicadores`
- `GET /api/resumo/substancias`
- `GET /api/resumo/csv`\n- `GET /api/dashboard/conversas-por-dia`\n- `GET /api/dashboard/encaminhamentos-por-dia`

Os CSVs de usuários e conversas não são expostos por endpoints públicos. Indicadores do arquivo de resultados são dados fictícios de demonstração, não evidência clínica.


## Dashboard diário do ReViver

As duas rotas novas analisam `conversas.csv`:
- `GET /api/dashboard/conversas-por-dia`: conta `id_conversa` distintos por data (usa a parte da data de `data_hora`).
- `GET /api/dashboard/encaminhamentos-por-dia`: conta conversas com `encaminhamento_realizado = sim` por data.

A atividade original de mercearia usa faturamento por dia. O ReViver não possui uma coluna financeira equivalente, então ela foi substituída pela contagem de encaminhamentos realizados. Isso não representa receita, taxa de sucesso nem resultado clínico. Os arquivos desta entrega são dados fictícios.

Teste manual:
```bash
curl http://127.0.0.1:8000/api/dashboard/conversas-por-dia
curl http://127.0.0.1:8000/api/dashboard/encaminhamentos-por-dia
```

## Dashboard analítico

Com a API em execução, consulte `GET /api/dashboard/indicadores`,
`GET /api/dashboard/conversas-por-dia` e
`GET /api/dashboard/encaminhamentos-por-dia`.
A interface fica em `paginas/dashboard.html`. Para servi-la localmente, execute
`python3 -m http.server 5500` na raiz do projeto e abra
`http://127.0.0.1:5500/paginas/dashboard.html`.

## Atualização dos dados do resumo

A página `paginas/resumo.html` lê os indicadores da rota `/api/resumo/indicadores` e a tabela de `/api/resumo/substancias`. As duas rotas leem novamente o arquivo `ReViver_resultados_por_substancia_900_LINHAS_DADOS_FICTICIOS.csv` a cada requisição (não há valores fixos no HTML).

Para atualizar:
1. Edite o CSV que fica na pasta principal do projeto (a mesma pasta de `backend/`), mantendo os cabeçalhos da primeira linha.
2. Salve o arquivo em CSV, usando vírgula ou ponto e vírgula como separador.
3. Na página Resumo dos dados, clique em **Atualizar dados**. O navegador fará uma nova requisição sem usar cache.
4. Se o backend não estiver ativo, o frontend tenta ler o CSV local servido junto com o site. Nesse caso, atualize o servidor local se ele estiver servindo uma cópia diferente da pasta editada.

O aviso de dados fictícios permanece intencional: esses registros são apenas demonstrativos e não representam pacientes nem eficácia clínica.
