"""REST API for the Design Agent Hub."""

from __future__ import annotations

import hmac
import io
import json
import os
import re
import zipfile

from fastapi import Depends, FastAPI, Header, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import __version__
from .agents.content_agent import ContentSpecialistAgent
from .agents.design_agent import DesignSpecialistAgent
from .catalog import get_catalog, search_catalog
from .connectors.canva import CanvaConnector
from .connectors.figma import FigmaConnector
from .figma_spec import FigmaSpecRequest, build_figma_spec
from .manager import manager as main_manager
from .planner import PlanRequest, create_plan
from .provider_router import recommend_tools
from .social_platforms import list_social_platforms
from .tool_registry import list_catalog_sources, list_tool_catalog, search_tool_catalog
from .catalog_sync import sync_catalog_source

app = FastAPI(
    title="NOVA — Networked Orchestration & Visual Automation",
    version=__version__,
    description="NOVA: provider-neutral design and social workflow agent with optional Canva/Figma adapters.",
)

_cors_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


class WorkflowPrepareRequest(BaseModel):
    request: str = Field(min_length=3, max_length=5000)
    audience: str | None = Field(default=None, max_length=500)
    platform: str | None = Field(default=None, max_length=100)
    constraints: list[str] = Field(default_factory=list, max_length=30)
    desired_format: str | None = Field(default=None, max_length=100)
    headline: str = Field(default="Ideas into editable designs", min_length=1, max_length=180)
    subheading: str = Field(default="Build, review, and refine with your workflow agent.", min_length=1, max_length=240)
    width: int = Field(default=1080, ge=320, le=4000)
    height: int = Field(default=1080, ge=320, le=4000)
    background: str = Field(default="#F8FAFC", pattern=r"^#[0-9a-fA-F]{6}$")
    accent: str = Field(default="#2563EB", pattern=r"^#[0-9a-fA-F]{6}$")
    foreground: str = Field(default="#0F172A", pattern=r"^#[0-9a-fA-F]{6}$")
    secondary: str = Field(default="#475569", pattern=r"^#[0-9a-fA-F]{6}$")


class ManagerDispatchRequest(BaseModel):
    task: str = Field(min_length=3, max_length=5000)


class ArtifactDownloadRequest(BaseModel):
    task: str = Field(min_length=3, max_length=1000)
    file_format: str = Field(pattern=r"^(svg|html)$")

class ArtifactPackageRequest(BaseModel):
    task: str = Field(min_length=3, max_length=1000)


class CanvaCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    width: int = Field(ge=40, le=8000)
    height: int = Field(ge=40, le=8000)
    user_approved: bool = False


class CanvaAutofillRequest(BaseModel):
    brand_template_id: str = Field(min_length=1, max_length=256)
    data: dict[str, object] = Field(min_length=1, max_length=100)
    title: str | None = Field(default=None, max_length=255)
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
        if os.getenv("APP_ENV", "development").lower() != "development":
            raise HTTPException(status_code=503, detail="API_BEARER_TOKEN must be configured outside development mode")
        return  # Local development only; never use this mode on a public network.
    supplied = (authorization or "").removeprefix("Bearer ").strip()
    if not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing bearer token")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "NOVA — Networked Orchestration & Visual Automation", "version": __version__}


@app.get("/agents", dependencies=[Depends(require_api_token)])
async def list_agents() -> dict[str, object]:
    """List the manager and registered specialist agents."""
    return main_manager.status()


@app.post("/manager/dispatch", dependencies=[Depends(require_api_token)])
async def manager_dispatch(payload: ManagerDispatchRequest) -> dict[str, object]:
    """Let the main manager select a registered specialist; current agents plan only."""
    return await main_manager.dispatch(payload.task)


@app.post("/artifacts/download", dependencies=[Depends(require_api_token)])
async def download_starter_artifact(request: ArtifactDownloadRequest) -> Response:
    """Return an editable starter SVG or HTML file as a download; no external service is called."""
    safe_name = re.sub(r"[^a-z0-9]+", "-", request.task.casefold()).strip("-")[:48] or "starter-asset"
    if request.file_format == "svg":
        content = DesignSpecialistAgent._make_svg(request.task)
        media_type = "image/svg+xml; charset=utf-8"
        filename = f"{safe_name}.svg"
    else:
        content = DesignSpecialistAgent._make_html(request.task)
        media_type = "text/html; charset=utf-8"
        filename = f"{safe_name}.html"
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": "attachment; filename=" + chr(34) + filename + chr(34)},
    )

@app.post("/artifacts/package", dependencies=[Depends(require_api_token)])
async def download_artifact_package(request: ArtifactPackageRequest) -> Response:
    """Bundle editable starter assets and a manifest into a ZIP download."""
    safe_name = re.sub(r"[^a-z0-9]+", "-", request.task.casefold()).strip("-")[:48] or "starter-package"
    copy = ContentSpecialistAgent()._starter_copy(request.task)
    files = {
        "index.html": DesignSpecialistAgent._make_html(request.task),
        "social-post.svg": DesignSpecialistAgent._make_svg(request.task),
        "content-brief.md": (
            "# Content starter\n\n"
            f"## Headline\n\n{copy['headline']}\n\n"
            f"## Supporting copy\n\n{copy['supporting_copy']}\n\n"
            f"## Call to action\n\n{copy['call_to_action']}\n\n"
            f"> {copy['disclosure']}\n"
        ),
        "README.txt": (
            "Design Agent Hub starter package\n"
            "Contains editable HTML and SVG starters plus draft copy.\n"
            "These are templates, not finished client-approved deliverables.\n"
            "Review accessibility, claims, links, licenses, and brand assets before use.\n"
        ),
        "manifest.json": json.dumps(
            {"task": request.task, "files": ["index.html", "social-post.svg", "content-brief.md", "README.txt"], "external_actions_performed": False},
            ensure_ascii=False,
            indent=2,
        ),
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for filename, file_content in files.items():
            archive.writestr(filename, file_content)
    return Response(
        content=buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=" + chr(34) + safe_name + ".zip" + chr(34)},
    )

@app.get("/catalog", dependencies=[Depends(require_api_token)])
async def catalog() -> dict[str, object]:
    return {"categories": get_catalog(), "category_count": len(get_catalog())}


@app.post("/tools/recommend", dependencies=[Depends(require_api_token)])
async def recommend_design_tools(payload: dict[str, object]) -> dict[str, object]:
    """Recommend free-first design providers for a task; never executes provider actions."""
    request = payload.get("task", "")
    connected = payload.get("connected_providers", [])
    if not isinstance(request, str) or len(request.strip()) < 3:
        raise HTTPException(status_code=422, detail="task must be a string of at least 3 characters")
    if not isinstance(connected, list) or not all(isinstance(item, str) for item in connected):
        raise HTTPException(status_code=422, detail="connected_providers must be a list of strings")
    return recommend_tools(request, connected)


@app.get("/catalog/search", dependencies=[Depends(require_api_token)])
async def catalog_search(q: str) -> dict[str, object]:
    return {"query": q, "matches": search_catalog(q)}


@app.post("/plan", dependencies=[Depends(require_api_token)])
async def plan(request: PlanRequest) -> dict[str, object]:
    result = await create_plan(request)
    return result.model_dump()


@app.post("/workflow/prepare", dependencies=[Depends(require_api_token)])
async def prepare_workflow(request: WorkflowPrepareRequest) -> dict[str, object]:
    """Prepare a plan and editable Figma spec; no provider writes occur in this endpoint."""
    plan = await create_plan(
        PlanRequest(
            request=request.request,
            audience=request.audience,
            platform=request.platform,
            constraints=request.constraints,
            desired_format=request.desired_format,
        )
    )
    spec = build_figma_spec(
        FigmaSpecRequest(
            title=request.request[:100],
            headline=request.headline,
            subheading=request.subheading,
            width=request.width,
            height=request.height,
            background=request.background,
            accent=request.accent,
            foreground=request.foreground,
            secondary=request.secondary,
        )
    )
    return {
        "status": "prepared",
        "execution_status": "plan_only",
        "plan": plan.model_dump(),
        "figma_plugin_spec": spec,
        "next_actions": [
            "Review the plan and generated design spec.",
            "Paste the spec into the local Figma plugin to create editable layers.",
            "For Canva, provide a brand_template_id and the template's exact autofill field names.",
            "Approve any external write or export explicitly before calling provider endpoints.",
        ],
    }


@app.post("/figma/plugin-spec", dependencies=[Depends(require_api_token)])
async def figma_plugin_spec(request: FigmaSpecRequest) -> dict[str, object]:
    """Return a design spec to paste into the local Figma plugin; does not modify any file."""
    return build_figma_spec(request)


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


@app.post("/connectors/canva/autofills", dependencies=[Depends(require_api_token)])
async def canva_autofill(request: CanvaAutofillRequest) -> dict[str, object]:
    if not request.user_approved:
        raise HTTPException(status_code=409, detail="Set user_approved=true only after the user explicitly confirms creating a design from this template.")
    try:
        return await CanvaConnector().create_autofill_job(request.brand_template_id, request.data, request.title)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Canva autofill request failed; verify template fields, plan eligibility, OAuth scopes, and rate limits.") from exc


@app.get("/connectors/canva/autofills/{job_id}", dependencies=[Depends(require_api_token)])
async def canva_get_autofill(job_id: str) -> dict[str, object]:
    try:
        return await CanvaConnector().get_autofill_job(job_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Canva autofill status request failed; check job ID and access permissions.") from exc


@app.get("/connectors/canva/exports/{export_id}", dependencies=[Depends(require_api_token)])
async def canva_get_export(export_id: str) -> dict[str, object]:
    try:
        return await CanvaConnector().get_export(export_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Canva export status request failed; check OAuth scopes and export ID.") from exc


@app.get("/social/platforms", dependencies=[Depends(require_api_token)])
async def social_platform_catalog() -> dict[str, object]:
    """List supported social platforms and their setup constraints; no live accounts are accessed."""
    return list_social_platforms()


@app.get("/connectors/status", dependencies=[Depends(require_api_token)])
async def connector_status() -> dict[str, object]:
    return {
        "figma": FigmaConnector().status().as_dict(),
        "canva": CanvaConnector().status().as_dict(),
        "model": {
            "primary_configured": bool(os.getenv("MODEL_BASE_URL") and os.getenv("MODEL_API_KEY") and os.getenv("MODEL_NAME")),
            "fallback_configured": bool(os.getenv("MODEL_FALLBACK_BASE_URL") and os.getenv("MODEL_FALLBACK_API_KEY") and os.getenv("MODEL_FALLBACK_NAME")),
            "strategy": "primary_then_fallback_then_deterministic",
            "note": "Optional OpenAI-compatible endpoints; credentials are never returned.",
        },
        "manager_memory": {
            "enabled": os.getenv("MANAGER_MEMORY_ENABLED", "false").strip().casefold() in {"1", "true", "yes", "on"},
            "storage": "local SQLite; compact task summaries only",
        },
    }


@app.get("/tools/catalog", dependencies=[Depends(require_api_token)])
async def tools_catalog(kind: str | None = None, no_key_only: bool = False) -> dict[str, object]:
    result = list_tool_catalog(kind=kind, no_key_only=no_key_only)
    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])
    return result


@app.get("/tools/catalog/search", dependencies=[Depends(require_api_token)])
async def tools_catalog_search(q: str, kind: str | None = None) -> dict[str, object]:
    if kind and kind not in {"builtin", "mcp", "api"}:
        raise HTTPException(status_code=422, detail="kind must be builtin, mcp, or api")
    return {"query": q, "kind": kind or "all", "matches": search_tool_catalog(q, kind)}



@app.get("/tools/catalog/sources", dependencies=[Depends(require_api_token)])
async def tools_catalog_sources() -> dict[str, object]:
    """List optional upstream MCP/API metadata feeds without fetching them."""
    return {"sources": list_catalog_sources(), "fetches_external_data": False}
\n    """Explicitly fetch one allowlisted upstream feed as bounded metadata; no code is installed or executed."""\n    try:\n        return await sync_catalog_source(source_id)\n    except ValueError as exc:\n        raise HTTPException(status_code=422, detail=str(exc)) from exc\n    except RuntimeError as exc:\n        raise HTTPException(status_code=502, detail=str(exc)) from exc\n

@app.get("/tools/catalog/sync", dependencies=[Depends(require_api_token)])
async def sync_upstream_catalog(source_id: str) -> dict[str, object]:
    """Explicitly fetch one allowlisted upstream feed as bounded metadata; no code is installed or executed."""
    try:
        return await sync_catalog_source(source_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
