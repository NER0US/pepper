# PepperGrok v3 — Local-First AI Shell for Grok.com

PepperGrok wraps **grok.com** in a tiny Electron shell so you can inject **Pepper**: your local memory + skills layer.  
- **Online** → Grok (SuperGrok) answers fast; Pepper injects a small, private context.  
- **Offline / Local skills** → handled locally (memory, `!ls`, `mv`, `cp`, etc.), never leaves your machine.

> No API spend. No cloud memory. Your context lives on disk.

---

## Features (v3)
- **One window**: full-bleed grok.com.
- **Control bar**: `[●][Online▼][Mem 6.2k/600k][Remember This][⋮]`.
- **Augmentation**: injects a short persona + top-K memories (token-capped).
- **Local skills**: `!ls`, `!mv`, `!cp`, `!cat`, `!tail` in a sandboxed path.
- **Remember This**: 1-click from selection; categories + pinning.
- **Failure-proof**: If the bridge is down, Online still works (no memory injection).

---

## Quickstart

### Prereqs
- Node 18+ / npm
- Python 3.10+ (if using the Python bridge)
- (Optional) **Ollama** for local LLM: https://ollama.com

### Install
```bash
git clone https://github.com/NER0US/pepper
cd pepper
npm install
```

### Dev Run

```bash
# 1) Start local model (optional)
ollama serve &  # optional

# 2) Start the bridge (choose JS or Python flavor later; see /bridge)
# Placeholder: will follow openapi.yaml in bridge/openapi.yaml

# 3) Start the Electron app
npm start
```

### Build

```bash
npm run build
```

---

## Modes

* **Online** (default): Submit to grok.com; Pepper augments with local memories (except `secrets`).
* **Offline**: Don’t hit grok.com; use local LLM for a reply; still saves to memory.
* **Classifier**: `!cmd`, fenced `bash`, `#offline/#local`, “remember this” → **local** regardless of toggle.

---

## Keyboard Shortcuts

* `Ctrl+Enter` — Send
* `Ctrl+.` — Open Skills Drawer
* `Ctrl+M` — Remember This
* `Ctrl+O` — Toggle Online/Offline
* `Ctrl+K` — Search memories (command palette)

---

## Privacy & Safety

* Memories are stored **locally** (`store/pepper_memory.jsonl` + vector index).
* **Secrets** category is **never** injected into Grok.
* Local skills run in a **sandboxed directory** with allow-listed commands and timeouts.

---

## Augmentation Format

```
<<<PEPPER_IDENTITY>>>
{persona}

<<<PEPPER_CONTEXT v1>>
- {snippet_1}  (#m123 people, score=0.84)
...
(Tokens≈{mem_tokens}; Pinned={n}; Categories={...})

<<<USER_MESSAGE>>
{user_text}

<<<INSTRUCTIONS>>
Answer concisely as Pepper. Use context if relevant. If conflict, ask a brief clarifier.
```

* Persona cap: **120 tokens**
* Memories cap: **600 tokens** (K=6 + pinned)
* **Secrets excluded** always

---

## Bridge API

OpenAPI spec: [`bridge/openapi.yaml`](./PepperGrok_v2/bridge/openapi.yaml)
Endpoints: `/status`, `/search`, `/remember`, `/memories`, `/identity`, `/skill`.

---

## Project Structure (target)

```
PepperGrok_v2/
  app/
    main.js                # Electron; CSP relax only for grok.com; preload on
    preload.js             # DOM hooks, classifier, augmentation injector
    renderer/
      ControlBar.(tsx|js)
      SkillsDrawer.(tsx|js)
  bridge/
    server.(py|js)         # Implements openapi.yaml
    openapi.yaml
  store/
    pepper_memory.jsonl
    pepper_vector.index
  scripts/
    import_openai_conversations.py
  docs/
    LAUNCH.md
```

---

## Troubleshooting

* **Grok loads but no overlay** → Check the bridge status; preload may be blocked (CSP not relaxed).
* **Offline disabled** → Bridge down; Online still works (no augmentation).
* **Token budget reached** → Engine trims least-recent non-pinned snippets; adjust caps in Settings.

---

## Roadmap (v3)

* ✅ Electron shell with surgical header rewrite
* ✅ Control bar v1
* ✅ Skills drawer
* ✅ Classifier + local routing
* ✅ Remember This + pin
* ✅ Memory store + search index
* ✅ Augmentation engine
* ✅ Bridge API v1
* ✅ Failure modes & fallbacks
* ✅ Settings modal

---

## License

MIT

---

# QA Checklist (map to Issues #1–#10)

**Pre-flight**
- Have `npm start` working; Grok page visible.
- Bridge running on `127.0.0.1:8000`.

1) **Electron shell / headers**
- Open DevTools → `document.currentScript` from preload exists.  
- Navigate to non-grok domain → confirm headers **not** altered.

2) **Control bar**
- Bar visible top-right; status dot present.  
- Toggle Online↔Offline updates label instantly.  
- Hover Memory → see snippet preview list.

3) **Skills drawer**
- `Ctrl+.` opens drawer; ESC closes.  
- Files tab shows sandbox path; run `!ls` via button and see output bubble.

4) **Classifier & routing**
- Type `!ls` in chat → local bubble appears; network tab shows **no** XHR/navigation to grok.com.  
- Type “remember this: …” → stored locally; toast confirms.

5) **Remember This modal**
- Select text on page → click **Remember This** → modal pre-filled.  
- Choose category `people`, pin it → save → toast shows id.

6) **Memory store + search**
- `GET /memories` returns the new entry with `pinned=true`.  
- `POST /search {query:"Who is Junior?"}` returns top-K including the new memory.

7) **Augmentation engine**
- Online: ask “Who is Junior?” → subtle indicator “Pepper added X (≈Y tks)”.  
- Hover indicator → category breakdown visible.  
- Confirm `secrets` items **never** appear.

8) **Bridge API v1**
- `GET /status` shows `bridge: up`, model info, caps.  
- `POST /skill` with `cmd: "ls"` returns `exit_code: 0`, bounded output.

9) **Failure modes**
- Stop bridge; keep app open.  
- Online still sends to grok.com (no indicator).  
- Offline mode disabled; tooltip explains “bridge down”.

10) **Settings modal**
- Change memory/token caps → next augmentation reflects limits.  
- Toggle **exclude secrets** → search results unchanged, augmentation excludes secrets.  
- Enable auto-prune; exceed size → oldest trimmed (confirm in `/memories`).

---

**a.** Want me to also produce a minimal `docs/LAUNCH.md` (launch order + health checks) to mirror your PDFs?
**b.** Or generate an OpenAPI-based Postman/Bruno collection JSON for quick local testing?
