/* Cliente da API do ReViver.
 * Tenta usar a API FastAPI (GET). Se ela não estiver iniciada, usa os CSVs
 * locais servidos junto com o frontend. Assim o site continua navegável sem
 * depender de uvicorn para carregar o catálogo educativo.
 * Execute o frontend por HTTP (ex.: python3 -m http.server 5500), não por file://.
 */
(function () {
  'use strict';
  const base = (window.REVIVER_API_BASE || 'http://127.0.0.1:8000').replace(/\/$/, '');
  const csvBase = window.location.pathname.includes('/paginas/') ? '../' : './';

  async function get(path) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 1800);
    try {
      const separator = path.includes('?') ? '&' : '?';
      const response = await fetch(`${base}${path}${separator}_atualizacao=${Date.now()}`, {
        method: 'GET',
        cache: 'no-store',
        headers: { Accept: 'application/json', 'Cache-Control': 'no-cache' },
        signal: controller.signal
      });
      if (!response.ok) throw new Error(`GET ${path}: HTTP ${response.status}`);
      return await response.json();
    } finally { clearTimeout(timeout); }
  }

  function parseCSV(text) {
    text = text.replace(/^\uFEFF/, '');
    // Detecta vírgula ou ponto e vírgula no cabeçalho.
    const primeiraLinha = text.split(/\r?\n/, 1)[0] || '';
    const virgulas = (primeiraLinha.match(/,/g) || []).length;
    const pontosVirgulas = (primeiraLinha.match(/;/g) || []).length;
    const delimiter = pontosVirgulas > virgulas ? ';' : ',';
    const rows = [];
    let row = [], cell = '', quoted = false;
    for (let i = 0; i < text.length; i++) {
      const ch = text[i], next = text[i + 1];
      if (ch === '"' && quoted && next === '"') { cell += '"'; i++; }
      else if (ch === '"') quoted = !quoted;
      else if (ch === delimiter && !quoted) { row.push(cell.trim()); cell = ''; }
      else if ((ch === '\n' || ch === '\r') && !quoted) {
        if (ch === '\r' && next === '\n') i++;
        row.push(cell.trim());
        if (row.some(value => value !== '')) rows.push(row);
        row = []; cell = '';
      } else cell += ch;
    }
    if (cell.length || row.length) { row.push(cell.trim()); if (row.some(value => value !== '')) rows.push(row); }
    if (!rows.length) return [];
    const headers = rows.shift().map(h => h.trim().replace(/^\uFEFF/, ''));
    return rows.map(values => Object.fromEntries(headers.map((h, i) => [h, values[i] ?? ''])));
  }

  async function getLocalCSV(file) {
    const response = await fetch(`${csvBase}${file}?_atualizacao=${Date.now()}`, {
      cache: 'no-store',
      headers: { Accept: 'text/csv,text/plain', 'Cache-Control': 'no-cache' }
    });
    if (!response.ok) throw new Error(`Não foi possível ler ${file}: HTTP ${response.status}`);
    return parseCSV(await response.text());
  }

  async function withFallback(apiPath, fallback) {
    try { return await get(apiPath); }
    catch (apiError) {
      try { return await fallback(); }
      catch (csvError) {
        console.error('API e CSV local indisponíveis.', { apiError, csvError });
        throw new Error('Não foi possível carregar os dados. Abra o frontend pelo servidor local e confira os arquivos CSV.');
      }
    }
  }

  async function substancias() {
    const data = await withFallback('/api/substancias', () => getLocalCSV('substancias.csv'));
    return Array.isArray(data) ? data : (data.itens || []);
  }
  async function clinicas() {
    const data = await withFallback('/api/clinicas', () => getLocalCSV('clinicas.csv'));
    return Array.isArray(data) ? { itens: data, dados_demonstrativos: true } : data;
  }
  async function indicadores() {
    return withFallback('/api/resumo/indicadores', async () => {
      const rows = await getLocalCSV('ReViver_resultados_por_substancia_900_LINHAS_DADOS_FICTICIOS.csv');
      const total = rows.length;
      const atingidas = rows.filter(r => String(r.meta_acompanhamento_atingida || '').trim().toLocaleLowerCase('pt-BR') === 'sim').length;
      const nomes = new Set(rows.map(r => r.substancia_registrada).filter(Boolean));
      return { dados_ficticios: true, aviso: 'DADOS FICTÍCIOS PARA TESTE. Não representam pacientes reais, eficácia clínica ou resultados de tratamento.', total_registros: total, total_substancias: nomes.size,
        metas_atingidas: atingidas, metas_parciais: rows.filter(r => String(r.meta_acompanhamento_atingida || '').trim().toLocaleLowerCase('pt-BR') === 'parcialmente').length, metas_nao_atingidas: rows.filter(r => ['não','nao'].includes(String(r.meta_acompanhamento_atingida || '').trim().toLocaleLowerCase('pt-BR'))).length, percentual_meta_atingida: total ? Number((atingidas * 100 / total).toFixed(1)) : 0 };
    });
  }
  async function resumoSubstancias() {
    return withFallback('/api/resumo/substancias', async () => {
      const rows = await getLocalCSV('ReViver_resultados_por_substancia_900_LINHAS_DADOS_FICTICIOS.csv');
      const groups = new Map();
      rows.forEach(r => {
        const name = String(r.substancia_registrada || 'Não informado');
        if (!groups.has(name)) groups.set(name, { substancia_registrada: name, registros: 0, metas_atingidas: 0, metas_parciais: 0, metas_nao_atingidas: 0 });
        const g = groups.get(name); g.registros++;
        const status = String(r.meta_acompanhamento_atingida || '').trim().toLocaleLowerCase('pt-BR');
        if (status === 'sim') g.metas_atingidas++;
        else if (status === 'parcialmente') g.metas_parciais++;
        else if (status === 'não' || status === 'nao') g.metas_nao_atingidas++;
      });
      return { dados_ficticios: true, itens: [...groups.values()].sort((a,b) => b.registros-a.registros) };
    });
  }

  window.ReviverAPI = {
    base, get, health: () => withFallback('/api/health', async () => ({ status: 'frontend-csv', servico: 'Catálogo local disponível' })),
    getSubstancias: substancias, getClinicas: clinicas,
    getIndicadores: indicadores, getResumoSubstancias: resumoSubstancias,
    getCSV: getLocalCSV
  };
})();
