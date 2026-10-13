"""Generate a small, editable Figma plugin spec from structured brief fields."""

from __future__ import annotations

from pydantic import BaseModel, Field


class FigmaSpecRequest(BaseModel):
    title: str = Field(default="Design Agent Hub", min_length=1, max_length=100)
    headline: str = Field(default="Ideas into editable designs", min_length=1, max_length=180)
    subheading: str = Field(default="Build, review, and refine with your workflow agent.", min_length=1, max_length=240)
    width: int = Field(default=1080, ge=320, le=4000)
    height: int = Field(default=1080, ge=320, le=4000)
    background: str = Field(default="#F8FAFC", pattern=r"^#[0-9a-fA-F]{6}$")
    accent: str = Field(default="#2563EB", pattern=r"^#[0-9a-fA-F]{6}$")
    foreground: str = Field(default="#0F172A", pattern=r"^#[0-9a-fA-F]{6}$")
    secondary: str = Field(default="#475569", pattern=r"^#[0-9a-fA-F]{6}$")


def build_figma_spec(req: FigmaSpecRequest) -> dict[str, object]:
    """Return a JSON spec accepted by the local Figma plugin; no external writes occur."""
    width, height = req.width, req.height
    margin = max(24, round(width * 0.067))
    headline_size = max(28, min(76, round(width * 0.059)))
    return {
        "frames": [
            {
                "name": req.title.strip()[:100],
                "width": width,
                "height": height,
                "background": req.background,
                "elements": [
                    {
                        "type": "text",
                        "name": "Brand label",
                        "text": req.title.strip()[:100].upper(),
                        "x": margin,
                        "y": max(32, round(height * 0.075)),
                        "width": width - margin * 2,
                        "height": 40,
                        "fontSize": max(14, round(width * 0.019)),
                        "weight": "medium",
                        "color": req.accent,
                    },
                    {
                        "type": "text",
                        "name": "Headline",
                        "text": req.headline.strip(),
                        "x": margin,
                        "y": round(height * 0.22),
                        "width": width - margin * 2,
                        "height": round(height * 0.24),
                        "fontSize": headline_size,
                        "weight": "medium",
                        "color": req.foreground,
                    },
                    {
                        "type": "rect",
                        "name": "Accent rule",
                        "x": margin,
                        "y": round(height * 0.50),
                        "width": max(72, round(width * 0.14)),
                        "height": max(6, round(width * 0.012)),
                        "color": req.accent,
                        "radius": 6,
                    },
                    {
                        "type": "text",
                        "name": "Supporting copy",
                        "text": req.subheading.strip(),
                        "x": margin,
                        "y": round(height * 0.57),
                        "width": width - margin * 2,
                        "height": round(height * 0.17),
                        "fontSize": max(16, min(32, round(width * 0.026))),
                        "color": req.secondary,
                    },
                ],
            }
        ]
    }
