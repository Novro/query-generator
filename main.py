"""
Query Builder - app desktop lokal pakai pywebview.

Install : pip install "pywebview[qt]"   (atau GTK via paket sistem)
Jalanin : python main.py
"""
import webbrowser
from urllib.parse import quote_plus

import webview

ENGINES = {
    "Google": {
        "base": "https://www.google.com/search?q=",
        "or": "+OR+",
        "filetype": "filetype:{}",
    },
    "Bing": {
        "base": "https://www.bing.com/search?q=",
        "or": "+OR+",
        "filetype": "filetype:{}",
    },
    "DuckDuckGo": {
        "base": "https://duckduckgo.com/?q=",
        "or": "+OR+",
        "filetype": "filetype:{}",
    },
    "Yahoo": {
        "base": "https://search.yahoo.com/search?p=",
        "or": "+OR+",
        "filetype": "filetype:{}",
    },
    "Yandex": {
        "base": "https://yandex.com/search/?text=",
        "or": "+%7C+",  # tanda |
        "filetype": "mime:{}",
    },
}

FILETYPES = ["docx", "xlsx", "pdf"]


def create(engine, keyword):
    cfg = ENGINES[engine]
    base_query = cfg["base"]
    keyword = [k.strip() for k in keyword if k.strip()]
    if not keyword:
        return []

    terms = [quote_plus(f'"{kw}"') for kw in keyword]

    and_q = base_query + "+".join(terms)
    and_op_q = base_query + "+AND+".join(terms)
    or_q = base_query + cfg["or"].join(terms)

    results = [
        {"label": "Semua keyword (implicit AND)", "url": and_q},
        {"label": "Semua keyword (AND eksplisit)", "url": and_op_q},
        {"label": "Salah satu keyword (OR)", "url": or_q},
    ]
    for ft in FILETYPES:
        op = cfg["filetype"].format(ft)
        results.append({"label": f"OR + {op}", "url": f"{or_q}+{op}"})
    results.append(
        {"label": "OR + site:drive.google.com", "url": or_q + "+site:drive.google.com"}
    )
    return results


class Api:
    def engines(self):
        return list(ENGINES.keys())

    def generate(self, engine, keywords_text):
        if engine not in ENGINES:
            return {"error": "Mesin pencari tidak dikenal."}
        results = create(engine, keywords_text.splitlines())
        if not results:
            return {"error": "Isi minimal satu keyword."}
        return {"results": results}

    def open_url(self, url):
        webbrowser.open(url)


HTML = r"""<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Query Builder</title>
<style>
  :root {
    --bg: #eef1f5;
    --panel: #ffffff;
    --ink: #1b2330;
    --muted: #667085;
    --line: #d5dbe4;
    --accent: #2a55d8;
    --accent-ink: #ffffff;
    --soft: #e4eafc;
    --err: #b42318;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #14181f;
      --panel: #1d232d;
      --ink: #e6eaf0;
      --muted: #8b95a5;
      --line: #313a48;
      --accent: #6f8fff;
      --accent-ink: #0f1420;
      --soft: #26304a;
      --err: #ff8a80;
    }
  }
  * { box-sizing: border-box; }
  html, body { height: 100%; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font: 15px/1.5 "Segoe UI", "SF Pro Text", system-ui, sans-serif;
  }
  .app {
    display: grid;
    grid-template-columns: minmax(280px, 360px) 1fr;
    gap: 20px;
    height: 100%;
    padding: 20px;
  }
  @media (max-width: 760px) {
    .app { grid-template-columns: 1fr; height: auto; }
  }
  .panel {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 20px;
    overflow: auto;
  }
  h1 { font-size: 20px; margin: 0 0 4px; letter-spacing: -0.01em; }
  .sub { color: var(--muted); margin: 0 0 20px; font-size: 14px; }
  label { display: block; font-weight: 600; margin: 16px 0 6px; font-size: 14px; }
  select, textarea {
    width: 100%;
    font: inherit;
    color: var(--ink);
    background: var(--bg);
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 9px 10px;
  }
  textarea { min-height: 150px; resize: vertical; }
  :focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
  .hint { color: var(--muted); font-size: 13px; margin-top: 4px; }
  button {
    font: inherit;
    cursor: pointer;
    border-radius: 6px;
    border: 1px solid var(--line);
    background: var(--panel);
    color: var(--ink);
    padding: 7px 12px;
  }
  button:hover { border-color: var(--accent); }
  button.primary {
    background: var(--accent);
    color: var(--accent-ink);
    border-color: var(--accent);
    font-weight: 600;
    width: 100%;
    margin-top: 20px;
    padding: 10px;
  }
  .head {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 12px; gap: 12px;
  }
  .head h2 { margin: 0; font-size: 16px; }
  .empty { color: var(--muted); padding: 40px 0; text-align: center; }
  .err { color: var(--err); margin-top: 12px; font-size: 14px; min-height: 1.2em; }
  .item {
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 10px;
  }
  .item .title { font-weight: 600; font-size: 14px; margin-bottom: 6px; }
  .url {
    font-family: Consolas, "SF Mono", monospace;
    font-size: 12.5px;
    background: var(--soft);
    border-radius: 6px;
    padding: 8px 10px;
    word-break: break-all;
    user-select: all;
  }
  .actions { display: flex; gap: 8px; margin-top: 8px; }
  .actions button { padding: 5px 10px; font-size: 13px; }
</style>
</head>
<body>
<div class="app">
  <section class="panel">
    <h1>Query Builder</h1>
    <p class="sub">Bikin beberapa variasi URL pencarian dari satu daftar keyword.</p>

    <label for="engine">Mesin pencari</label>
    <select id="engine"></select>
    <div class="hint" id="engineHint"></div>

    <label for="kw">Keyword</label>
    <textarea id="kw" placeholder="laporan keuangan&#10;2025&#10;anggaran"></textarea>
    <div class="hint">Satu keyword per baris. Spasi di dalam keyword dibiarkan.</div>

    <button class="primary" id="go">Buat query</button>
    <div class="err" id="err" role="alert"></div>
  </section>

  <section class="panel">
    <div class="head">
      <h2 id="count">Hasil</h2>
      <button id="copyAll" hidden>Salin semua</button>
    </div>
    <div id="out"><div class="empty">Isi keyword di kiri, lalu klik Buat query.</div></div>
  </section>
</div>

<script>
  const $ = (id) => document.getElementById(id);
  const HINTS = {
    Yandex: "Yandex pakai | untuk OR dan mime: untuk tipe file.",
    Yahoo: "Operator filetype: di Yahoo kadang diabaikan.",
  };
  let current = [];

  function copyText(text) {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    document.execCommand("copy");
    ta.remove();
  }

  function flash(btn, text) {
    const old = btn.textContent;
    btn.textContent = text;
    setTimeout(() => (btn.textContent = old), 1200);
  }

  function render(results) {
    current = results;
    $("count").textContent = `Hasil (${results.length})`;
    $("copyAll").hidden = false;
    $("out").innerHTML = "";
    results.forEach((r) => {
      const el = document.createElement("div");
      el.className = "item";
      el.innerHTML = `
        <div class="title"></div>
        <div class="url"></div>
        <div class="actions">
          <button data-a="copy">Salin</button>
          <button data-a="open">Buka di browser</button>
        </div>`;
      el.querySelector(".title").textContent = r.label;
      el.querySelector(".url").textContent = r.url;
      el.querySelector('[data-a="copy"]').onclick = (e) => {
        copyText(r.url);
        flash(e.target, "Tersalin");
      };
      el.querySelector('[data-a="open"]').onclick = () =>
        pywebview.api.open_url(r.url);
      $("out").appendChild(el);
    });
  }

  async function generate() {
    $("err").textContent = "";
    const res = await pywebview.api.generate($("engine").value, $("kw").value);
    if (res.error) {
      $("err").textContent = res.error;
      return;
    }
    render(res.results);
  }

  window.addEventListener("pywebviewready", async () => {
    const names = await pywebview.api.engines();
    const sel = $("engine");
    names.forEach((name) => {
      const o = document.createElement("option");
      o.value = name;
      o.textContent = name;
      sel.appendChild(o);
    });
    const updateHint = () => ($("engineHint").textContent = HINTS[sel.value] || "");
    sel.onchange = updateHint;
    updateHint();

    $("go").onclick = generate;
    $("kw").addEventListener("keydown", (e) => {
      if (e.ctrlKey && e.key === "Enter") generate();
    });
    $("copyAll").onclick = (e) => {
      copyText(current.map((r) => r.url).join("\n"));
      flash(e.target, "Tersalin");
    };
  });
</script>
</body>
</html>
"""


if __name__ == "__main__":
    webview.create_window(
        "Query Builder",
        html=HTML,
        js_api=Api(),
        width=1000,
        height=680,
        min_size=(720, 480),
    )
    webview.start()