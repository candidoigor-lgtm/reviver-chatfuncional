/* Consulta perguntas pré-definidas e mostra o resultado calculado pelo Python. */
(() => {
  const form = document.getElementById("chatDadosForm");
  if (!form) return;

  const select = document.getElementById("chatPergunta");
  const button = document.getElementById("chatDadosEnviar");
  const resultado = document.getElementById("chatDadosResultado");
  const aviso = document.getElementById("chatDadosAviso");
  const API = (window.REVIVER_API_BASE || "http://127.0.0.1:8000").replace(/\/$/, "");

  function mostrarObjeto(dados) {
    resultado.replaceChildren();
    const titulo = document.createElement("h3");
    titulo.textContent = "Resultado encontrado no CSV";
    resultado.append(titulo);
    const lista = document.createElement("dl");
    Object.entries(dados || {}).forEach(([chave, valor]) => {
      if (chave === "dados_ficticios") return;
      const termo = document.createElement("dt");
      termo.textContent = chave.replaceAll("_", " ").replace(/^./, c => c.toUpperCase());
      const definicao = document.createElement("dd");
      definicao.textContent = typeof valor === "object" && valor !== null
        ? JSON.stringify(valor, null, 2)
        : String(valor);
      lista.append(termo, definicao);
    });
    resultado.append(lista);
    resultado.hidden = false;
  }

  async function carregarPerguntas() {
    try {
      const resposta = await fetch(`${API}/api/chat/perguntas`, { headers: { Accept: "application/json" } });
      if (!resposta.ok) throw new Error("Não foi possível carregar as perguntas.");
      const perguntas = await resposta.json();
      select.replaceChildren(new Option("Selecione uma pergunta", ""));
      perguntas.forEach(pergunta => select.add(new Option(pergunta, pergunta)));
    } catch (erro) {
      select.replaceChildren(new Option("Não foi possível carregar. Verifique se a API está ligada.", ""));
      aviso.textContent = "Inicie o backend para carregar as perguntas.";
      aviso.hidden = false;
    }
  }

  form.addEventListener("submit", async event => {
    event.preventDefault();
    if (!select.value || button.disabled) return;
    button.disabled = true;
    button.textContent = "Consultando...";
    resultado.hidden = true;
    aviso.hidden = true;
    try {
      const resposta = await fetch(`${API}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ pergunta: select.value })
      });
      const dados = await resposta.json();
      if (!resposta.ok) throw new Error(dados.detail || "Falha ao consultar os dados.");
      if (dados.resultado) mostrarObjeto(dados.resultado);
      else {
        resultado.textContent = dados.aviso || "Escolha uma pergunta disponível.";
        resultado.hidden = false;
      }
      if (dados.explicacao) {
        const explicacao = document.createElement("p");
        explicacao.className = "chat-dados-explicacao";
        explicacao.textContent = dados.explicacao;
        resultado.append(explicacao);
      }
      if (dados.aviso || dados.aviso_dados) {
        aviso.textContent = [dados.aviso, dados.aviso_dados].filter(Boolean).join(" ");
        aviso.hidden = false;
      }
    } catch (erro) {
      aviso.textContent = erro.message || "Não foi possível conectar à API.";
      aviso.hidden = false;
    } finally {
      button.disabled = false;
      button.textContent = "Consultar dados";
    }
  });

  carregarPerguntas();
})();
