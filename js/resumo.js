const statusEl = document.getElementById("apiStatus");
const refreshButton = document.getElementById("refreshSummary");
const cardsEl = document.getElementById("summaryCards");
const tableBody = document.getElementById("substanceRows");
const noticeEl = document.getElementById("dataNotice");

function setStatus(message, error = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle("error", error);
}
function numberBR(value) {
  return Number(value || 0).toLocaleString("pt-BR");
}
function card(label, value, detail) {
  const article = document.createElement("article");
  article.className = "summary-card";
  const h = document.createElement("h3"); h.textContent = label;
  const strong = document.createElement("strong"); strong.textContent = value;
  const p = document.createElement("p"); p.textContent = detail;
  article.append(h, strong, p);
  return article;
}
async function carregarResumo() {
  refreshButton.disabled = true;
  setStatus("Carregando dados do ReViver…");
  try {
    const [resumo, substResp] = await Promise.all([
      window.ReviverAPI.getIndicadores(),
      window.ReviverAPI.getResumoSubstancias()
    ]);
    const itens = Array.isArray(substResp) ? substResp : (substResp.itens || []);
    cardsEl.replaceChildren(
      card("Registros demonstrativos", numberBR(resumo.total_registros), "Linhas no CSV fictício"),
      card("Substâncias no conjunto", numberBR(resumo.total_substancias), "Categorias distintas"),
      card("Metas marcadas como atingidas", `${numberBR(resumo.metas_atingidas)} (${String(resumo.percentual_meta_atingida ?? 0).replace(".", ",")}%)`, "Contagem do campo do CSV; não mede eficácia clínica")
    );
    noticeEl.textContent = resumo.aviso || "Dados demonstrativos do CSV. Não representam resultados clínicos reais.";
    tableBody.replaceChildren();
    for (const item of itens) {
      const tr = document.createElement("tr");
      for (const value of [item.substancia_registrada, item.registros, item.metas_atingidas, item.metas_parciais, item.metas_nao_atingidas]) {
        const td = document.createElement("td"); td.textContent = value ?? "—"; tr.appendChild(td);
      }
      tableBody.appendChild(tr);
    }
    setStatus(`Dados atualizados: ${numberBR(resumo.total_registros)} registros lidos do CSV.`);
  } catch (error) {
    setStatus(error.message || "Não foi possível carregar os dados.", true);
    cardsEl.replaceChildren();
    tableBody.replaceChildren();
    noticeEl.textContent = "Confira se o frontend foi aberto por um servidor HTTP e se os arquivos CSV estão na pasta principal.";
  } finally {
    refreshButton.disabled = false;
  }
}
refreshButton.addEventListener("click", carregarResumo);
carregarResumo();
