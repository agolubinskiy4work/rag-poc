// ==UserScript==
// @name         Local RAG Sidebar Assistant
// @namespace    local-rag-mvp
// @version      0.1.0
// @description  Right-side page-aware assistant backed by local FastAPI + Ollama RAG
// @author       local
// @match        *://*/*
// @grant        none
// ==/UserScript==

(function () {
  "use strict";

  // ===== Config (edit only these values) =====
  const BACKEND_BASE_URL = "http://127.0.0.1:8000";
  const REQUEST_TIMEOUT_MS = 30000;
  const URL_PATTERNS = [
    "https://example.com/*",
    "https://*.atlassian.net/wiki/*",
  ];

  const matchesPattern = (url, pattern) => {
    const escaped = pattern.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*");
    return new RegExp(`^${escaped}$`).test(url);
  };

  if (!URL_PATTERNS.some((pattern) => matchesPattern(window.location.href, pattern))) {
    return;
  }

  const root = document.createElement("div");
  root.id = "local-rag-sidebar-root";
  root.innerHTML = `
    <style>
      #local-rag-sidebar { position: fixed; top: 0; right: 0; width: 360px; height: 100vh; z-index: 2147483647; background: #111827; color: #e5e7eb; box-shadow: -2px 0 10px rgba(0,0,0,.25); display: flex; flex-direction: column; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
      #local-rag-sidebar.collapsed { transform: translateX(328px); transition: transform .2s ease; }
      .local-rag-head { display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; border-bottom: 1px solid #374151; }
      .local-rag-logo { font-size: 13px; font-weight: 700; }
      #local-rag-toggle { background: #374151; color: white; border: none; border-radius: 6px; padding: 4px 8px; cursor: pointer; }
      #local-rag-messages { flex: 1; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 10px; }
      .local-rag-msg { padding: 8px 10px; border-radius: 8px; font-size: 13px; line-height: 1.4; white-space: pre-wrap; }
      .local-rag-msg.user { background: #2563eb; color: #fff; align-self: flex-end; max-width: 90%; }
      .local-rag-msg.assistant { background: #1f2937; max-width: 95%; }
      .local-rag-citations { margin-top: 8px; display: flex; flex-direction: column; gap: 6px; }
      .local-rag-citations a { color: #93c5fd; text-decoration: underline; font-size: 12px; }
      .local-rag-input { display: flex; gap: 8px; border-top: 1px solid #374151; padding: 10px; }
      #local-rag-question { flex: 1; border: 1px solid #4b5563; background: #111827; color: #e5e7eb; border-radius: 8px; padding: 8px; font-size: 13px; }
      #local-rag-send { border: none; border-radius: 8px; background: #16a34a; color: #fff; padding: 8px 10px; cursor: pointer; }
    </style>
    <div id="local-rag-sidebar">
      <div class="local-rag-head">
        <div class="local-rag-logo">🧠 Local RAG Assistant</div>
        <button id="local-rag-toggle" type="button">⇔</button>
      </div>
      <div id="local-rag-messages"></div>
      <div class="local-rag-input">
        <input id="local-rag-question" type="text" placeholder="Ask about this page..." />
        <button id="local-rag-send" type="button">Send</button>
      </div>
    </div>
  `;
  document.body.appendChild(root);

  const sidebar = document.getElementById("local-rag-sidebar");
  const messages = document.getElementById("local-rag-messages");
  const input = document.getElementById("local-rag-question");
  const send = document.getElementById("local-rag-send");
  const toggle = document.getElementById("local-rag-toggle");

  const addMessage = (text, role, citations = []) => {
    const msg = document.createElement("div");
    msg.className = `local-rag-msg ${role}`;
    msg.textContent = text;

    if (role === "assistant" && citations.length > 0) {
      const citeWrap = document.createElement("div");
      citeWrap.className = "local-rag-citations";
      citations.forEach((c) => {
        if (!c.url_or_path) return;
        const a = document.createElement("a");
        a.href = c.url_or_path;
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        a.textContent = `${c.source_type || "source"}: ${c.title || c.url_or_path}`;
        citeWrap.appendChild(a);
      });
      msg.appendChild(citeWrap);
    }

    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
  };

  const ask = async () => {
    const question = input.value.trim();
    if (!question) return;
    input.value = "";
    addMessage(question, "user");

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
      const response = await fetch(`${BACKEND_BASE_URL}/api/chat/page`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          page_url: window.location.href,
          page_html: document.documentElement.outerHTML,
          page_title: document.title,
          timestamp: new Date().toISOString(),
        }),
        signal: controller.signal,
      });

      if (!response.ok) {
        addMessage(`Backend error ${response.status}: ${await response.text()}`, "assistant");
        return;
      }

      const data = await response.json();
      if (!data || typeof data.answer_text !== "string") {
        addMessage("Malformed JSON response from backend.", "assistant");
        return;
      }
      addMessage(data.answer_text, "assistant", Array.isArray(data.citations) ? data.citations : []);
    } catch (err) {
      const message = err && err.name === "AbortError"
        ? "Request timed out while contacting local backend."
        : "Backend unreachable. Verify FastAPI is running and CORS is configured.";
      addMessage(message, "assistant");
    } finally {
      clearTimeout(timeout);
    }
  };

  send.addEventListener("click", ask);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") ask();
  });
  toggle.addEventListener("click", () => {
    sidebar.classList.toggle("collapsed");
  });
})();
