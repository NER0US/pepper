# PepperGrok v2

Hybrid AI companion bridging Grok's reasoning with Ollama-powered memory.

## Features

- FastAPI bridge with `/query`, `/remember`, `/memories`, `/status`, and `/speak` routes.
- Emotionally weighted memory system stored at `~/bje/pepper_dir/identity/pepper_memory.json`.
- Optional pyttsx3 voice output and hourly heartbeat log.
- Minimal single-page UI served from `/ui` with chat, memory capture, and status pulse.
- Launch script for macOS (`start_pepper.command`) and a migration utility for historical OpenAI logs.

## Quickstart

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.server:app --reload
```

Visit http://localhost:8000/ui to interact with Pepper.

### Example API Requests

```bash
curl -X POST http://localhost:8000/query \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "Pepper, how was your day?", "mode": "online"}'

curl -X POST http://localhost:8000/remember \
  -H 'Content-Type: application/json' \
  -d '{"text": "Morning tea ritual complete", "category": "ritual"}'
```

## Configuration

Edit `app/config.json` to provide your Grok API key, toggle heartbeat or voice, and choose the Ollama model name.
