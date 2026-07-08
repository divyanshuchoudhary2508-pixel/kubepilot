"""
KubePilot backend entrypoint.

A small, single-purpose FastAPI app: three routes total
(GET /health, POST /validate, POST /fix). No database, no auth.
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.fix import router as fix_router
from app.routes.health import router as health_router
from app.routes.validate import router as validate_router

app = FastAPI(
    title="KubePilot API",
    description="Deterministic Kubernetes manifest validator and fixer.",
    version="1.0.0",
)

# Netlify frontend origin(s). Set FRONTEND_ORIGIN on Render to your deployed
# Netlify URL (e.g. https://kubepilot.netlify.app). Local dev origins are
# included by default so `npm run dev` works out of the box.
_default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
_configured_origin = os.getenv("FRONTEND_ORIGIN")
allow_origins = _default_origins + ([_configured_origin] if _configured_origin else [])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(validate_router)
app.include_router(fix_router)
