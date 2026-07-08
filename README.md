# KubePilot

A browser-based Kubernetes manifest validator. Paste or upload YAML, get
errors/warnings with line numbers and suggestions, and download a
deterministically fixed version. No login, no database, no AI — just rules.

## Stack

- **Frontend:** React + Vite + TypeScript + Tailwind + Monaco Editor → deployed on Netlify
- **Backend:** FastAPI + PyYAML + ruamel.yaml → deployed on Render

## Project structure

```
frontend/
  src/
    components/   # Navbar, UploadBox, MonacoEditor, ValidationResults, etc.
    pages/         # HomePage — the single page
    hooks/         # useManifestValidation — owns all app state
    services/      # typed Axios client (validate/fix/health)
    types/         # mirrors backend Pydantic schemas
    utils/         # severity styling, file download, placeholder manifest

backend/
  app/
    main.py         # FastAPI app + CORS
    routes/         # health.py, validate.py, fix.py
    validators/      # the actual rule engine
      line_finder.py    # recovers real line numbers from parsed YAML
      required_fields.py
      deployment.py
      service.py
      best_practices.py
      engine.py          # orchestrates checks, computes score
      fixers.py           # deterministic /fix patches (ruamel round-trip)
    schemas/         # Pydantic request/response models
    utils/            # YAML parsing helper
```

## Local development

**Backend:**
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Runs at `http://localhost:8000`. Interactive docs at `/docs`.

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env   # points at localhost:8000 by default
npm run dev
```
Runs at `http://localhost:5173`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/validate` | `{ content }` → errors, warnings, passed checks, score |
| POST | `/fix` | `{ content }` → `fixed_content` + list of applied fixes |

## Deployment

**Backend → Render:** `render.yaml` at the repo root defines the service
(`rootDir: backend`, `uvicorn app.main:app`). Connect the repo in Render and
it will pick this up automatically. After deploying, note the Render URL.

**Frontend → Netlify:** `netlify.toml` at the repo root sets `base: frontend`
and `publish: dist`. In Netlify's site settings, set the environment variable
`VITE_API_BASE_URL` to your Render backend URL.

**Wire CORS:** back on Render, set `FRONTEND_ORIGIN` to your Netlify URL so
the backend accepts requests from it.

## What this deliberately doesn't do

No auth, no database, no history, no multi-page routing, no AI-based fixes,
no cluster connection. `/fix` only applies changes that have exactly one
correct answer (e.g. `replicas: 1`, a selector copied from existing template
labels, default resource requests/limits). Anything requiring a judgment call
— an image tag, a container name, probe paths — stays flagged for you to
decide, not guessed.
