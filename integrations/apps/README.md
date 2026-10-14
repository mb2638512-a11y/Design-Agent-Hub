# NOVA local-app adapters: GenOffice + ArtCraft

NOVA means **Networked Orchestration & Visual Automation**. The Python project is the coordinator; GenOffice and ArtCraft remain separate upstream applications.

## What is verified from project descriptions

- [GenOffice](https://github.com/genspark-ai/genoffice) is public and its core is Apache-2.0, with an exception: the `ee/` directory uses separate enterprise terms. It includes Docs, Sheets, Slides, PDF and Markdown editors, with local file editing and AI features. Its README describes a CLI and agent/MCP integration. Do not copy the `ee/` directory into this repository.
- [ArtCraft app lineup](https://getartcraft.com/apps) currently lists 13 editors: PhotoCraft, VectorCraft, FilmCraft, LightCraft, PdfCraft, EffectCraft, DesignCraft, FigCraft, WordCraft, SoundCraft, DeckCraft, CADCraft and GridCraft. The project describes CLI/JSON/MCP control channels and local-first workflows. Check each individual repository's current license, maturity, releases and control protocol before installing.

These projects are free/open-source, but **free does not mean every AI feature is free**: GenOffice may require a network-backed account or a user-provided model key for AI actions. Upstream app compatibility and stability vary; several ArtCraft apps are alpha/in development.

## Safe integration plan

1. Keep NOVA's `app` catalog as metadata. Catalog entries are not proof an app is installed or verified.
2. Install upstream apps from their official release pages on the user's machine. Avoid copying all source trees into this repository: that duplicates large codebases, makes updates difficult and complicates license/security review.
3. For each installed app, check its official CLI help and MCP/JSON documentation. Use a per-app adapter that accepts a structured task and a workspace path, validates file types and paths, runs only a locally installed executable, captures exit code/output, and returns artifact paths.
4. Do not invent a shared ArtCraft CLI command: each app's exact command schema must be verified against that app's current release.
5. Connect only verified adapters to NOVA's tool registry. Mark each adapter `installed`, `smoke_tested` and `verified` separately; never infer those statuses from catalog presence.
6. Restrict file access to a dedicated workspace. Require explicit approval before overwriting/deleting files, exporting private documents, publishing, or sending content to a cloud AI provider.
7. Pin releases, record licenses and checksums, and run apps in a separate user account/container where practical.

## Suggested staged rollout

- **Stage A — registry:** discover/search the 14 entries from REST or MCP; no installation or code execution.
- **Stage B — GenOffice:** install the official release, inspect its shipped CLI/agent instructions, and smoke-test DOCX/XLSX/PPTX/PDF/Markdown tasks on disposable sample files.
- **Stage C — ArtCraft:** add one app at a time, starting with PhotoCraft, VectorCraft, DesignCraft and PdfCraft; test opening, editing, saving and export before enabling any write adapter.
- **Stage D — agent integration:** create a reviewed adapter for each verified interface, add tests, and expose only the necessary tools to NOVA. Use explicit user confirmation for consequential operations.

## Current implementation status

- Catalog entries: added to `src/design_agent_hub/tool_registry.py`.
- REST discovery: `GET /tools/catalog?kind=app` and `GET /tools/catalog/search?q=PhotoCraft&kind=app` (API token required).
- MCP discovery: `list_tool_hubs(kind="app")` and `search_tool_hubs(query="PhotoCraft", kind="app")`.
- Actual app source trees, desktop installers, live CLI/MCP adapters, and gateway deployments: **not included or installed by this change**.
