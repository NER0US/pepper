# GitHub Issues for Pepper

## Issue 1 — Electron Shell: load grok.com with surgical header rewrites
**Labels:** enhancement, priority:high, area:electron, security  \
**Story Points:** 3

**Description:**
Create `BrowserWindow` with `preload`. Use `session.webRequest.onHeadersReceived` to relax `Content-Security-Policy`, `X-Frame-Options`, and `COOP/COEP` **only** for `https://grok.com/*`. Keep `contextIsolation: true`.

**Acceptance Criteria:**
- grok.com loads inside the app; preload runs.
- Header changes scoped to grok.com only.
- `contextIsolation` remains `true`; no `webSecurity: false`.

---

## Issue 2 — Control Bar v1 (top-right, 48px, semi-transparent)
**Labels:** enhancement, area:ui, ux  \
**Story Points:** 3

**Description:**
Render: `[●][Online▼][Mem 6.2k/600k][Remember This][⋮]` with the status dot **leftmost**. Tooltips for status and memory.

**Acceptance Criteria:**
- Toggle flips Online/Offline instantly.
- Status tooltip shows bridge/ollama/latency.
- Memory hover lists chosen snippets (first ~80 chars).
- Bar does not occlude Grok input.

---

## Issue 3 — Skills Drawer (360px slide-over, `Ctrl+.`)
**Labels:** enhancement, area:ui, local-skills  \
**Story Points:** 5

**Description:**
Right-side drawer with tabs **Files / Notes / History** + search bar.

**Acceptance Criteria:**
- Opens via `Ctrl+.`; closes via ESC/close.
- Files: sandbox path, quick actions (`!ls`, `!cat`, `!mv`, `!cp`).
- Notes: add memory note with category; inline edit existing entries.
- History: last 10 local actions with timestamps.

---

## Issue 4 — Classifier + Local Routing
**Labels:** enhancement, area:preload, local-skills  \
**Story Points:** 5

**Description:**
Client-side rules: `!cmd`, fenced `bash`, `#offline/#local`, “remember this” → route to **/skill** and **do not** submit to Grok.

**Acceptance Criteria:**
- `!ls` renders a chat bubble labeled **local**.
- Destructive ops require confirmation; sandbox enforced.
- Non-local prompts pass through unchanged.

---

## Issue 5 — “Remember This” + Pin
**Labels:** enhancement, area:ui, memory  \
**Story Points:** 3

**Description:**
Button opens modal: textarea (pre-filled from selection), category dropdown, **Pin to top-K** toggle.

**Acceptance Criteria:**
- Save persists memory; toast with id.
- `secrets` category saved but never used in augmentation.
- Pinned items surface first (within token cap).

---

## Issue 6 — Memory Store + Search Index
**Labels:** enhancement, area:bridge, memory, infra  \
**Story Points:** 8

**Description:**
JSONL store (`pepper_memory.jsonl`) + vector index. Import `conversations.json`. Endpoints `/memories` (list/search) and `/search` (top-K).

**Acceptance Criteria:**
- Schema matches spec; import preserves `conv_id`/`source`.
- `/search?query=...` returns top-K ≤ 50ms (warm).
- Rotation/backup policy documented.

---

## Issue 7 — Augmentation Engine (budgeted, deduped, transparent)
**Labels:** enhancement, area:preload, augmentation, perf  \
**Story Points:** 8

**Description:**
Retrieve K=6 (+ pinned), dedupe, trim; persona ≤120 tokens; memories ≤600 tokens.

**Acceptance Criteria:**
- Indicator: “Pepper added X (≈Y tks)”; hover shows per-category counts.
- `secrets` excluded; pinned respected.
- Overflow trims least-recent non-pinned first.

---

## Issue 8 — Bridge API v1
**Labels:** enhancement, area:bridge, api  \
**Story Points:** 5

**Description:**
Implement `/status`, `/search`, `/remember`, `/memories`, `/skill`, `/identity` per OpenAPI (`bridge/openapi.yaml`).

**Acceptance Criteria:**
- `/status` reports bridge+model+latency.
- `/skill` execs allow-listed cmds in sandbox with timeouts & output caps.
- `/identity` get/set persona; persisted.

---

## Issue 9 — Failure Modes & Fallbacks
**Labels:** enhancement, resilience, ux  \
**Story Points:** 3

**Description:**
If bridge down → Online works **without augmentation**; show warning toast. Offline disabled with tooltip.

**Acceptance Criteria:**
- Bridge down: Grok chat usable.
- Input shows “No memory injection (bridge down)”.
- Offline send disabled; tooltip explains.

---

## Issue 10 — Settings Modal
**Labels:** enhancement, area:ui, settings  \
**Story Points:** 5

**Description:**
Tabs: Identity, Memory, Sandbox, Hotkeys, Privacy (exclude secrets, auto-prune).

**Acceptance Criteria:**
- Changing caps affects next augmentation.
- Auto-prune trims oldest when over limit.
- “Exclude secrets” strictly enforced.
