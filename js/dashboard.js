(() => {
  'use strict';
  const API = 'http://127.0.0.1:8000';
  const $ = (id) => document.getElementById(id);
  const fmt = (n) => Number(n || 0).toLocaleString('pt-BR');
  const pct = (n, total) => total ? (100 * n / total) : 0;
  const esc = (s) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

  async function get(path) {
    const separator = path.includes('?') ? '&' : '?';
    const response = await fetch(`${API}${path}${separator}_atualizacao=${Date.now()}`, { cache: 'no-store', headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' } });
    if (!response.ok) { let detail = ''; try { detail = (await response.json()).detail || ''; } catch (_) {} throw new Error(detail || `Falha ao consultar ${path} (${response.status})`); }
    return response.json();
  }
  function drawBars(target, items, key, colorLabel) {
    const el = $(target);
    if (!items || !items.length) { el.innerHTML = '<p class="chart-empty">Sem registros disponíveis para este gráfico.</p>'; return; }
    const data = items.slice(-14), max = Math.max(1, ...data.map(x => Number(x[key] || 0)));
    const W = 620, H = 230, left = 38, right = 12, top = 16, bottom = 48;
    const plotH = H - top - bottom, plotW = W - left - right, gap = 8, barW = Math.max(7, (plotW - gap * data.length) / data.length);
    let bars = '', labels = '', grid = '';
    for (let i=0;i<=4;i++){const y=top+plotH-(plotH*i/4);grid += `<line x1="${left}" y1="${y}" x2="${W-right}" y2="${y}" stroke="#285477" stroke-opacity=".55"/><text x="${left-8}" y="${y+4}" text-anchor="end" fill="#8eb9dc" font-size="10">${Math.round(max*i/4)}</text>`;}
    data.forEach((d,i)=>{const v=Number(d[key]||0), x=left+i*(barW+gap), h=plotH*v/max, y=top+plotH-h;bars+=`<rect x="${x}" y="${y}" width="${barW}" height="${Math.max(1,h)}" rx="4" fill="#25a8f5"><title>${esc(d.data)}: ${v} ${colorLabel}</title></rect>`;if(i%Math.max(1,Math.ceil(data.length/7))===0||i===data.length-1){const label=String(d.data).slice(5);labels+=`<text x="${x+barW/2}" y="${H-20}" text-anchor="middle" fill="#8eb9dc" font-size="10">${esc(label)}</text>`;}});
    el.innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Gráfico de ${colorLabel} por dia">${grid}${bars}${labels}</svg>`;
  }
  function bars(target, rows, totalKey, labelKey) {
    const el=$(target); if(!rows.length){el.innerHTML='<p class="chart-empty">Sem dados.</p>';return;}
    el.innerHTML=rows.map(r=>{const n=Number(r.value||0), width=Math.max(0,Math.min(100,Number(r.percent||0)));return `<div class="breakdown-item"><div class="breakdown-top"><span>${esc(r.label)}</span><strong>${fmt(n)} · ${width.toFixed(1)}%</strong></div><div class="track"><span style="width:${width}%"></span></div></div>`;}).join('');
  }
  function detailTable(d){
    const u=d.usuarios,c=d.conversas,k=d.clinicas;
    const rows=[['Usuários cadastrados',u.total,'—'],['Consentimentos confirmados',u.consentimento_confirmado,`${u.taxa_consentimento}%`],['Conversas registradas',c.total,'—'],['Conversas que precisam de profissional',c.precisam_profissional,`${c.percentual_precisam_profissional}%`],['Conversas classificadas com atenção',c.com_atencao,`${c.percentual_com_atencao}%`],['Encaminhamentos realizados',c.encaminhamentos_realizados,`${c.taxa_encaminhamento}%`],['Encaminhamentos não realizados',c.encaminhamentos_nao_realizados,`${pct(c.encaminhamentos_nao_realizados,c.total).toFixed(1)}%`],['Clínicas ativas',k.ativas,`${k.taxa_ativas}%`],['Clínicas aguardando confirmação',k.aguardando_confirmacao,`${pct(k.aguardando_confirmacao,k.total).toFixed(1)}%`],['Clínicas encerradas',k.encerradas,`${pct(k.encerradas,k.total).toFixed(1)}%`]];
    $('detailRows').innerHTML=rows.map(r=>`<tr><td>${esc(r[0])}</td><td>${fmt(r[1])}</td><td>${r[2]}</td></tr>`).join('');
  }
  async function load(){
    $('apiStatus').textContent='Carregando dados…';$('apiStatus').classList.remove('error');
    try{
      const [d,convs,refs]=await Promise.all([get('/api/dashboard/indicadores'),get('/api/dashboard/conversas-por-dia'),get('/api/dashboard/encaminhamentos-por-dia')]);
      const u=d.usuarios,c=d.conversas,k=d.clinicas;
      $('mUsers').textContent=fmt(u.total);$('mUsersDetail').textContent=`${fmt(u.interessados)} interessados · ${fmt(u.familiares)} familiares`;
      $('mChats').textContent=fmt(c.total);$('mChatsDetail').textContent=`${c.percentual_precisam_profissional}% precisam de profissional`;
      $('mReferrals').textContent=fmt(c.encaminhamentos_realizados);$('mReferralsDetail').textContent=`${c.taxa_encaminhamento}% do total de conversas`;
      $('mClinics').textContent=`${fmt(k.ativas)} / ${fmt(k.total)}`;$('mClinicsDetail').textContent=`${k.taxa_ativas}% com atendimento ativo`;
      $('dataNotice').textContent=d.aviso;
      drawBars('conversationsChart',convs.itens,'total_conversas','conversas');
      drawBars('referralsChart',refs.itens,'total_encaminhamentos','encaminhamentos');
      bars('usersBreakdown',[
        {label:'Interessados',value:u.interessados,percent:pct(u.interessados,u.total)},
        {label:'Familiares',value:u.familiares,percent:pct(u.familiares,u.total)},
        {label:'Em acompanhamento',value:u.em_acompanhamento,percent:pct(u.em_acompanhamento,u.total)}
      ]);
      bars('clinicsBreakdown',[
        {label:'Ativas',value:k.ativas,percent:pct(k.ativas,k.total)},
        {label:'Aguardando confirmação',value:k.aguardando_confirmacao,percent:pct(k.aguardando_confirmacao,k.total)},
        {label:'Encerradas',value:k.encerradas,percent:pct(k.encerradas,k.total)}
      ]);
      detailTable(d);$('apiStatus').textContent='API conectada · Dados atualizados';
    }catch(err){console.error(err);$('apiStatus').textContent='Não foi possível carregar';$('apiStatus').classList.add('error');$('dataNotice').textContent=`${err.message}. Confira se o backend está rodando na porta 8000.`;['conversationsChart','referralsChart','usersBreakdown','clinicsBreakdown'].forEach(id=>$(id).innerHTML='<p class="chart-empty">Inicie o backend e clique em atualizar.</p>');$('detailRows').innerHTML='<tr><td colspan="3">Dados indisponíveis.</td></tr>';}
  }
  $('refreshDashboard').addEventListener('click',load);load();
})();
