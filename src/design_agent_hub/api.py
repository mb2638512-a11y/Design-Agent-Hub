"""REST API for the Design Agent Hub."""

from __future__ import annotations

import hmac
import os

from fastapi import Depends, FastAPI, Header, HTTPException

from . import __version__
from .catalog import get_catalog, search_catalog
from .connectors.canva import CanvaConnector
from .connectors.figma import FigmaConnector
from .planner import PlanRequest, create_plan

app = FastAPI(
    title="Design Agent Hub",
    version=__version__,
    description="Provider-neutral design workflow planner with optional Canva/Figma adapters.",
)


async def require_api_token(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("API_BEARER_TOKEN", "").strip()
    if not expected:
        return  # Local development only; configure a token before exposing the API.
    supplied = (authorization or "").removeprefix("Bearer ").strip()
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing bearer token")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "Design Agent Hub", "version": __version__}


@app.get("/catalog", dependencies=[Depends(require_api_token)])
async def catalog() -> dict[str, object]:
    return {"categories": get_catalog(), "category_count": len(get_catalog())}


@app.get("/catalog/search", dependencies=[Depends(require_api_token)])
async def catalog_search(q: str) -> dict[str, object]:
    return {"query": q, "matches": search_catalog(q)}


@app.post("/plan", dependencies=[Depends(require_api_token)])
async def plan(request: PlanRequest) -> dict[str, object]:
    result = await create_plan(request)
    return result.model_dump()


@app.get("/connectors/status", dependencies=[Depends(require_api_token)])
async def connector_status() -> dict[str, object]:
    return {
        "figma": FigmaConnector().status().as_dict(),
        "canva": CanvaConnector().status().as_dict(),
        "model": {
            "configured": bool(os.getenv("MODEL_BASE_URL") and os.getenv("MODEL_API_KEY") and os.getenv("MODEL_NAME")),
            "note": "Optional OpenAI-compatible model endpoint; no model credentials are bundled.",
        },
    }
