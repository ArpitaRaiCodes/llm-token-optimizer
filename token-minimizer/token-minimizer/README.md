# Token Minimizer

Shrink your text's token count **locally**, using small Qwen models — same
meaning, fewer tokens. Useful before sending prompts to a paid, remote LLM
where you're billed per token.

Paste text → see its token count → click **Minimize token** → a locally
running Qwen model (0.5B / 1.5B / 3B, your choice based on your hardware)
rewrites it to be leaner without losing meaning → copy it or export the
before/after as a `.md` file.

Everything runs on your own machine. No text ever leaves your computer.

## How it works

```
┌────────────┐   POST /api/count      ┌─────────────┐
│  Frontend  │ ─────────────────────▶ │   FastAPI   │──▶ tiktoken (local)
│ React+Vite │                        │   backend   │
│            │   POST /api/compress   │             │──▶ Ollama ──▶ Qwen model
└────────────┘ ◀───────────────────── └─────────────┘
```

- **Token counting** uses `tiktoken` (cl100k_base) — this approximates what
  you'd actually be billed on downstream by most modern LLM APIs, which is
  the number that matters for this tool's purpose.
- **Compression** is done by a small Qwen2.5 model running locally through
  [Ollama](https://ollama.com), guided by a system prompt that instructs it
  to preserve all facts/intent and only cut filler and redundancy.
- The backend never sends your text anywhere except to your own local Ollama
  instance.

## Model options

| Model | Approx. RAM needed | Best for |
|---|---|---|
| `qwen2.5:0.5b` | ~2 GB | Low-end laptops, fastest |
| `qwen2.5:1.5b` | ~4 GB | Good quality/speed balance |
| `qwen2.5:3b` | ~6 GB | Best compression quality |

You only need to pull the size(s) you plan to use — pick whichever fits your
system.

## Quick start (Docker — recommended)

Requires [Docker](https://docs.docker.com/get-docker/) installed.

```bash
git clone https://github.com/<your-username>/token-minimizer.git
cd token-minimizer

docker compose up -d --build

# In a separate terminal, pull the model(s) you want:
./scripts/setup_models.sh          # pulls the 0.5B default
# or: ./scripts/setup_models.sh all
```

Open **http://localhost:5173**.

> GPU acceleration: uncomment the `deploy` block for the `ollama` service in
> `docker-compose.yml` if you have `nvidia-container-toolkit` set up.

## Manual / local dev setup (no Docker)

**1. Install and run Ollama**
```bash
# https://ollama.com/download
ollama serve
ollama pull qwen2.5:0.5b
```

**2. Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

**3. Frontend**
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** (Vite proxies `/api` to the backend on `:8000`).

## Running tests

```bash
cd backend
pip install -r requirements.txt
pytest
```

## Project structure

```
token-minimizer/
├── backend/
│   ├── main.py                # FastAPI routes
│   ├── services/
│   │   ├── ollama_client.py   # talks to Ollama's REST API
│   │   ├── tokenizer.py       # token counting (tiktoken)
│   │   └── compress.py        # compression prompt + safety checks
│   ├── models/schemas.py      # request/response contracts
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/ (ModelSelector, ResultPanel)
│   │   └── api/client.js
│   └── package.json
├── scripts/setup_models.sh
└── docker-compose.yml
```

## API reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Backend + Ollama reachability check |
| `GET` | `/api/models` | Lists allowed models and whether each is pulled |
| `POST` | `/api/count` | `{ text }` → `{ tokens, characters }` |
| `POST` | `/api/compress` | `{ text, model }` → compressed text + stats |

Rate limits: 60/min on `/count`, 15/min on `/compress` (adjust in `main.py`
for your deployment).

## Design notes / safety behavior

- If the model's output isn't actually shorter (in tokens) than the input,
  the API falls back to returning the original text rather than reporting a
  fake "win."
- Input is capped at 20,000 characters per request to keep response times
  reasonable on small local models — raise `MAX_INPUT_CHARS` in
  `backend/models/schemas.py` if your hardware can handle more.
- CORS is wide open (`*`) for easy local use; **lock `allow_origins` down to
  your real frontend domain before deploying this publicly.**

## License

MIT — see [LICENSE](LICENSE).
