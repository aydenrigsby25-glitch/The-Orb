"""Web entrypoint. Vercel detects the FastAPI `app` in app.py automatically.

Run locally:   uvicorn app:app --reload    then open http://127.0.0.1:8000
"""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from orb import AskRequest, AskResponse, Orb

ROOT = Path(__file__).parent

app = FastAPI(title="The ORB", docs_url=None, redoc_url=None)
orb = Orb()


@app.post("/api/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    return orb.ask(req)


@app.get("/api/health")
def health():
    return {"status": "awake"}


# On Vercel, public/index.html is served from the CDN before this route is reached.
# Locally (uvicorn), this route serves the page.
@app.get("/", include_in_schema=False)
def home():
    page = ROOT / "public" / "index.html"
    if page.exists():
        return FileResponse(page)
    return RedirectResponse("/index.html")


# Locally, serve everything in public/ (logo, icons). Vercel serves public/ itself,
# and its docs say not to mount it there, so this only runs off Vercel.
if not os.environ.get("VERCEL"):
    app.mount("/", StaticFiles(directory=ROOT / "public"), name="public")
