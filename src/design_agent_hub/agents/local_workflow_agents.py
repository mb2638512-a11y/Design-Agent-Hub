"""Free-first, lightweight specialists for local creative and office workflows.

These agents produce structured plans only. They do not claim to launch apps or
perform edits until a reviewed local CLI/MCP adapter is installed and verified.
"""
from __future__ import annotations

from typing import ClassVar


class TaskPlanningAgent:
    """Reusable deterministic specialist that plans work without model/API calls."""

    id: str = "task_planner"
    name: str = "Task Planning Agent"
    description: str = "Creates a lightweight plan for a specific local creative workflow."
    capabilities: ClassVar[list[str]] = []
    recommended_apps: ClassVar[list[str]] = []

    def match_score(self, task: str) -> int:
        normalized = task.casefold()
        return sum(7 for term in self.capabilities if term in normalized)

    async def run(self, task: str) -> dict[str, object]:
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "result_type": "local_workflow_plan",
            "execution_status": "plan_only_adapter_not_verified",
            "task": task,
            "recommended_apps": list(self.recommended_apps),
            "workflow": [
                "Inspect the requested input and confirm the desired output format.",
                "Select an installed, license-reviewed local tool or a verified MCP/CLI adapter.",
                "Process locally where supported to avoid cloud compute and per-call AI charges.",
                "Validate the generated artifact and preserve the original input.",
                "Return the output path, validation notes, and any steps that still need human review.",
            ],
            "limitations": [
                "This agent creates a plan; it does not claim that an external application was launched or that a file was edited.",
                "App execution requires an installed app and a reviewed, verified adapter.",
                "AI inference may have separate usage limits or costs even when the editing app is free.",
            ],
        }


class OfficeSpecialistAgent(TaskPlanningAgent):
    id = "office"
    name = "Office Agent"
    description = "Plans local document, office-suite, and Markdown workflows."
    capabilities = ["genoffice", "office document", "word document", "docx", "write a report", "markdown document", "edit a document"]
    recommended_apps = ["GenOffice"]


class ImageSpecialistAgent(TaskPlanningAgent):
    id = "image"
    name = "Image Agent"
    description = "Plans raster image editing, cleanup, resizing, and export workflows."
    capabilities = ["photocraft", "edit image", "image editing", "photo editing", "remove background", "resize image", "image retouch"]
    recommended_apps = ["PhotoCraft"]


class VectorSpecialistAgent(TaskPlanningAgent):
    id = "vector"
    name = "Vector Design Agent"
    description = "Plans editable vector, logo, icon, and illustration workflows."
    capabilities = ["vectorcraft", "vector logo", "vector illustration", "svg icon", "svg logo", "vector graphics", "edit svg"]
    recommended_apps = ["VectorCraft"]


class VideoSpecialistAgent(TaskPlanningAgent):
    id = "video"
    name = "Video Agent"
    description = "Plans video editing, motion graphics, and export workflows."
    capabilities = ["filmcraft", "video editing", "edit a video", "video montage", "shorts video", "reel video", "motion graphics"]
    recommended_apps = ["FilmCraft", "EffectCraft"]


class AudioSpecialistAgent(TaskPlanningAgent):
    id = "audio"
    name = "Audio Agent"
    description = "Plans audio cleanup, sound design, and audio export workflows."
    capabilities = ["soundcraft", "audio editing", "edit audio", "sound effect", "audio cleanup", "podcast audio", "sound design"]
    recommended_apps = ["SoundCraft"]


class SpreadsheetSpecialistAgent(TaskPlanningAgent):
    id = "spreadsheet"
    name = "Spreadsheet Agent"
    description = "Plans spreadsheet, table, formula, and data-cleaning workflows."
    capabilities = ["spreadsheet", "excel file", "xlsx", "spreadsheet formula", "clean this data", "gridcraft", "data table"]
    recommended_apps = ["GenOffice", "GridCraft"]


class PdfSpecialistAgent(TaskPlanningAgent):
    id = "pdf"
    name = "PDF Agent"
    description = "Plans PDF editing, conversion, and document review workflows."
    capabilities = ["pdfcraft", "edit pdf", "merge pdf", "split pdf", "convert to pdf", "pdf form", "pdf document"]
    recommended_apps = ["PdfCraft", "GenOffice"]
