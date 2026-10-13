"""REST API for the Design Agent Hub."""

from __future__ import annotations

import hmac
import os

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

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


class CanvaCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    width: int = Field(ge=40, le=8000)
    height: int = Field(ge=40, le=8000)
    user_approved: bool = False


class CanvaExportRequest(BaseModel):
    design_id: str = Field(min_length=1, max_length=256)
    file_format: str = "png"
    user_approved: bool = False


class FigmaExportRequest(BaseModel):
    file_key: str = Field(min_length=1, max_length=256)
    node_ids: list[str] = Field(min_length=1, max_length=100)
    image_format: str = "png"



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


@app.get("/connectors/figma/files/{file_key}", dependencies=[Depends(require_api_token)])
async def figma_file(file_key: str) -> dict[str, object]:
    try:
        return await FigmaConnector().get_file(file_key)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Figma request failed; check credentials, scopes, file access, and rate limits.") from exc


@app.post("/connectors/figma/export", dependencies=[Depends(require_api_token)])
async def figma_export(request: FigmaExportRequest) -> dict[str, object]:
    try:
        return await FigmaConnector().export_node_images(request.file_key, request.node_ids, request.image_format)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Figma export request failed; check credentials, scopes, file access, and rate limits.") from exc


@app.post("/connectors/canva/designs", dependencies=[Depends(require_api_token)])
async def canva_create(request: CanvaCreateRequest) -> dict[str, object]:
    if not request.user_approved:
        raise HTTPException(status_code=409, detail="Set user_approved=true only after the user explicitly confirms creating a Canva design.")
    if request.width * request.height > 25_000_000:
        raise HTTPException(status_code=422, detail="Custom design area must not exceed 25,000,000 pixels.")
    try:
        return await CanvaConnector().create_design(request.title, request.width, request.height)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Canva create-design request failed; check OAuth scopes, account access, and rate limits.") from exc


@app.post("/connectors/canva/exports", dependencies=[Depends(require_api_token)])
async def canva_export(request: CanvaExportRequest) -> dict[str, object]:
    if not request.user_approved:
        raise HTTPException(status_code=409, detail="Set user_approved=true only after the user explicitly confirms starting an export.")
    try:
        return await CanvaConnector().start_export(request.design_id, request.file_format)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Canva export request failed; check OAuth scopes, design access, and rate limits.") from exc


@app.get("/connectors/canva/exports/{export_id}", dependencies=[Depends(require_api_token)])
async def canva_get_export(export_id: str) -> dict[str, object]:
    try:
        return await CanvaConnector().get_export(export_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Canva export status request failed; check OAuth scopes and export ID.") from exc


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
