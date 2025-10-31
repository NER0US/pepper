```markdown
# NER0US/pepper
## PepperGrok v3 — Local-First AI Shell for Grok.com
**PepperGrok wraps grok.com in a tiny Electron shell so you can inject Pepper: your local memory + skills layer.**
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
ollama serve & # optional
# 2) Start the bridge
# 3) Start the Electron app
npm start
```
### Build
```bash
npm run build
```
### Modes
• Online (default): Submit to grok.com; Pepper augments with local memories (except secrets).  
• Offline: Don’t hit grok.com; use local LLM for a reply; still saves to memory.  
• Classifier: !cmd, fenced bash, #offline/#local, “remember this” → local regardless of toggle.

### Keyboard Shortcuts
• Ctrl+Enter — Send  
• Ctrl+. — Open Skills Drawer  
• Ctrl+M — Remember This  
• Ctrl+O — Toggle Online/Offline  
• Ctrl+K — Search memories (command palette)

### Privacy & Safety
• Memories are stored locally (store/pepper_memory.jsonl + vector index).  
• Secrets category is never injected into Grok.  
• Local skills run in a sandboxed directory with allow-listed commands and timeouts.

### Augmentation Format
```
<>
{persona}
<<<PEPPER_CONTEXT v1>>
- {snippet_1} (#m123 people, score=0.84)
...
(Tokens≈{mem_tokens}; Pinned={n}; Categories={...})
<
{user_text}
<
Answer concisely as Pepper. Use context if relevant. If conflict, ask a brief clarifier.
```
• Persona cap: 120 tokens  
• Memories cap: 600 tokens (K=6 + pinned)  
• Secrets excluded always

### Bridge API
OpenAPI spec: bridge/openapi.yaml  
Endpoints: /status, /search, /remember, /memories, /identity, /skill.

### Project Structure
```
PepperGrok_v2/
  app/
    main.js
    preload.js
    renderer/
      ControlBar.(tsx|js)
      SkillsDrawer.(tsx|js)
  bridge/
    server.(py|js)
    openapi.yaml
  store/
    pepper_memory.jsonl
    pepper_vector.index
  scripts/
    import_openai_conversations.py
  docs/
    LAUNCH.md
```

### Troubleshooting
• Grok loads but no overlay → Check bridge status; preload may be blocked (CSP).  
• Offline disabled → Bridge down; Online still works.  
• Token budget reached → Engine trims least-recent non-pinned snippets.

### Roadmap (v3)
• ✅ Electron shell  
• ✅ Control bar v1  
• ✅ Skills drawer  
• ✅ Classifier + local routing  
• ✅ Remember This + pin  
• ✅ Memory store + search index  
• ✅ Augmentation engine  
• ✅ Bridge API v1  
• ✅ Failure modes & fallbacks  
• ✅ Settings modal

### License
MIT

### QA Checklist (Issues #1–#10)
#### Pre-flight
• npm start working; Grok page visible.  
• Bridge running on 127.0.0.1:8000.  
1. Electron shell → DevTools: document.currentScript exists.  
2. Control bar → Visible, toggle works.  
3. Skills drawer → Ctrl+. opens.  
4. Classifier → !ls → local response.  
5. Remember This → Modal pre-filled.  
6. Memory store → /memories returns entry.  
7. Augmentation → “Pepper added X tks”.  
8. Bridge API → /status shows bridge: up.  
9. Failure modes → Bridge down → Online still works.  
10. Settings → Caps update augmentation.

Built with 100+ hours, 13 PDFs, 150MB of soul. ❤️


