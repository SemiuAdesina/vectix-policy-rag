const chat = document.getElementById("chat");
const input = document.getElementById("question");
const askBtn = document.getElementById("askBtn");
let inFlight = false;
let lastSubmittedQuery = "";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function uniqueItems(items) {
  return [...new Set((items || []).filter(Boolean))];
}

function cleanSnippetText(value) {
  const lines = String(value || "")
    .split("\n")
    .map(line => line.trim())
    .filter(Boolean)
    .filter(line => line !== "---")
    .filter(line => !/^\|?[\-\s:|]+\|?$/.test(line))
    .map(line => {
      if (line.startsWith("|")) {
        line = line.split("|").map(part => part.trim()).filter(Boolean).join(" ");
      }
      return line.replace(/^#{1,6}\s*/, "").replaceAll("**", "").replaceAll("`", "");
    });
  const joined = lines.join(" ").replace(/\s+/g, " ").trim();
  return joined.length > 280 ? `${joined.slice(0, 280)}...` : joined;
}

function renderMessage(role, content, sources = [], chunks = []) {
  const wrap = document.createElement("div");
  wrap.className = "message";
  const uniqueSources = uniqueItems(sources).slice(0, 3);
  const seenSources = new Set();
  const uniqueChunks = [];
  (chunks || []).forEach(chunk => {
    const source = String(chunk?.source || "Unknown source");
    if (seenSources.has(source)) return;
    seenSources.add(source);
    uniqueChunks.push({ source, content: cleanSnippetText(chunk?.content || "") });
  });
  const pills = uniqueSources.map(source => `<span class="pill">${escapeHtml(source)}</span>`).join("");
  const snippetHtml = uniqueChunks.slice(0, 2).map(chunk => `
    <div class="snippet">
      <div class="snippet-source">${escapeHtml(chunk.source)}</div>
      <div class="snippet-body">${escapeHtml(chunk.content)}</div>
    </div>
  `).join("");
  if (role.toLowerCase() === "assistant") {
    wrap.innerHTML = `
      <div class="role">${escapeHtml(role)}</div>
      <div class="answer-text">${escapeHtml(content)}</div>
      ${pills ? `<div class="evidence-shell"><div class="label">Cited Sources</div><div class="pills">${pills}</div></div>` : ""}
      ${snippetHtml ? `<details class="evidence"><summary>View supporting evidence</summary>${snippetHtml}<div class="hint">Evidence is collapsible to keep the chat clean during demos.</div></details>` : ""}
    `;
  } else {
    wrap.innerHTML = `<div class="role">${escapeHtml(role)}</div><div>${escapeHtml(content)}</div>`;
  }
  chat.prepend(wrap);
}

async function askQuestion() {
  const query = input.value.trim();
  if (!query || inFlight || query === lastSubmittedQuery) return;
  inFlight = true;
  askBtn.disabled = true;
  renderMessage("User", query);
  input.value = "";
  lastSubmittedQuery = query;
  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const result = await response.json();
    renderMessage("Assistant", result.answer || "No answer returned.", result.sources || [], result.chunks || []);
  } catch (error) {
    renderMessage("Assistant", `Request failed: ${error}`);
    lastSubmittedQuery = "";
  } finally {
    inFlight = false;
    askBtn.disabled = false;
  }
}

askBtn.addEventListener("click", askQuestion);
input.addEventListener("keydown", event => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
    askQuestion();
  }
});
document.querySelectorAll(".chip").forEach(chip => {
  chip.addEventListener("click", () => {
    input.value = chip.textContent;
    input.focus();
  });
});
