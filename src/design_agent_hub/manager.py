"""Main manager agent, specialist registry, and bounded multi-agent orchestration."""

from __future__ import annotations

import asyncio

from .agents.base import SpecialistAgent
from .agents.coding_agent import CodingSpecialistAgent
from .agents.content_agent import ContentSpecialistAgent
from .agents.delivery_agent import DeliverySpecialistAgent
from .agents.design_agent import DesignSpecialistAgent
from .agents.quality_agent import QualitySpecialistAgent
from .agents.research_agent import ResearchSpecialistAgent
from .agents.social_media_agent import SocialMediaSpecialistAgent


class AgentRegistry:
    """Registry that lets specialists be added without changing the dispatcher."""

    def __init__(self, agents: list[SpecialistAgent] | None = None) -> None:
        self._agents: dict[str, SpecialistAgent] = {}
        for agent in agents or []:
            self.register(agent)

    def register(self, agent: SpecialistAgent) -> None:
        agent_id = agent.id.strip()
        if not agent_id:
            raise ValueError("Agent id must not be empty")
        if agent_id in self._agents:
            raise ValueError(f"Agent already registered: {agent_id}")
        self._agents[agent_id] = agent

    def list_agents(self) -> list[dict[str, object]]:
        return [
            {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "capabilities": list(agent.capabilities),
            }
            for agent in self._agents.values()
        ]

    def rank(self, task: str) -> list[tuple[int, SpecialistAgent]]:
        """Return matching specialists from highest to lowest score.

        Python's stable sort preserves registration order for ties, making routing
        deterministic and easier to debug.
        """
        return sorted(
            ((agent.match_score(task), agent) for agent in self._agents.values()),
            key=lambda pair: pair[0],
            reverse=True,
        )

    def choose(self, task: str) -> SpecialistAgent | None:
        ranked = self.rank(task)
        if not ranked or ranked[0][0] <= 0:
            return None
        return ranked[0][1]

    def get(self, agent_id: str) -> SpecialistAgent | None:
        return self._agents.get(agent_id)


class MainManagerAgent:
    """Routes focused requests and coordinates bounded specialist workflows."""

    id = "manager"
    name = "Main Manager Agent"
    agent_timeout_seconds = 60
    max_task_characters = 20_000
    max_domain_specialists = 3
    _complex_markers = (
        "end-to-end", "end to end", "complete package", "full project",
        "from start to finish", "launch the whole", "entire workflow",
        "automate", "across all", "manage everything", "whole campaign",
        "research and create", "design and build", "create and publish",
        "plan and execute", "audit and fix", "build and test",
    )
    _multi_step_markers = (",", ";", " and ", " then ", " followed by ")
    _support_agents = ("quality", "delivery")

    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or AgentRegistry(
            [
                DesignSpecialistAgent(),
                CodingSpecialistAgent(),
                ContentSpecialistAgent(),
                ResearchSpecialistAgent(),
                SocialMediaSpecialistAgent(),
                QualitySpecialistAgent(),
                DeliverySpecialistAgent(),
            ]
        )

    def status(self) -> dict[str, object]:
        agents = self.registry.list_agents()
        return {
            "manager_id": self.id,
            "manager_name": self.name,
            "registered_agent_count": len(agents),
            "agents": agents,
            "routing_mode": "capability_scoring_with_bounded_collaboration",
            "execution_limits": {
                "max_task_characters": self.max_task_characters,
                "agent_timeout_seconds": self.agent_timeout_seconds,
                "max_domain_specialists": self.max_domain_specialists,
            },
            "multi_agent_workflows": True,
            "operating_principles": [
                "Complete safe, useful parts instead of refusing an entire mixed request unnecessarily.",
                "Route focused tasks to the strongest matching specialist; collaborate only for multi-step or cross-domain tasks.",
                "Use bounded execution so one stalled specialist cannot block the whole workflow indefinitely.",
                "Distinguish returned plans or artifacts from external actions verified by a connected tool.",
                "Require authorization for consequential external writes, publication, deletion, messaging, or spending.",
                "Report partial success and failed specialists clearly; never invent successful execution.",
            ],
        }

    async def _run_with_timeout(self, agent: SpecialistAgent, task: str) -> dict[str, object]:
        """Run one specialist with a timeout; caller handles and reports failures."""
        return await asyncio.wait_for(agent.run(task), timeout=self.agent_timeout_seconds)

    @staticmethod
    def _safe_failure(exc: BaseException) -> dict[str, object]:
        if isinstance(exc, TimeoutError):
            return {
                "status": "timed_out",
                "error": "Specialist exceeded the manager execution time limit.",
            }
        return {
            "status": "failed",
            "error": f"{type(exc).__name__}: specialist failed; inspect server logs for details.",
        }

    async def dispatch(self, task: str) -> dict[str, object]:
        cleaned = " ".join(task.split()) if isinstance(task, str) else ""
        if len(cleaned) < 3:
            return {
                "status": "invalid_request",
                "manager": self.name,
                "message": "Task must contain at least 3 non-whitespace characters.",
            }
        if len(cleaned) > self.max_task_characters:
            return {
                "status": "task_too_large",
                "manager": self.name,
                "max_task_characters": self.max_task_characters,
                "message": "Split this request into smaller tasks so specialists can process it reliably.",
            }

        ranked = [(score, agent) for score, agent in self.registry.rank(cleaned) if score > 0]
        if not ranked:
            return {
                "status": "no_matching_agent",
                "manager": self.name,
                "task": cleaned,
                "registered_agents": self.registry.list_agents(),
                "message": "No specialist currently matches this task. Try describing the desired outcome and domain, or register a suitable specialist.",
            }

        primary_score, primary = ranked[0]
        domain_matches = [
            agent for score, agent in ranked
            if agent.id not in self._support_agents and score > 0
        ]
        normalized = f" {cleaned.casefold()} "
        has_multiple_steps = any(mark in normalized for mark in self._multi_step_markers)
        complex_task = any(marker in normalized for marker in self._complex_markers) or (
            len(domain_matches) >= 2 and has_multiple_steps
        )

        if not complex_task:
            try:
                result = await self._run_with_timeout(primary, cleaned)
            except BaseException as exc:
                if isinstance(exc, (KeyboardInterrupt, SystemExit, asyncio.CancelledError)):
                    raise
                failure = self._safe_failure(exc)
                return {
                    "status": "agent_failed" if failure["status"] == "failed" else "agent_timed_out",
                    "manager": self.name,
                    "task": cleaned,
                    "selected_agent": {"id": primary.id, "name": primary.name, "score": primary_score},
                    "failure": failure,
                    "retry_guidance": "Retry once, simplify the task, or use a different specialist if the problem persists.",
                }
            return {
                "status": "delegated",
                "manager": self.name,
                "task": cleaned,
                "selected_agent": {"id": primary.id, "name": primary.name, "score": primary_score},
                "workflow_mode": "single_specialist",
                "result_contract": "A returned result is not proof of an external action unless a connected tool confirms it.",
                "result": result,
            }

        # Select only relevant domain specialists, then append review and handoff roles.
        selected: list[SpecialistAgent] = []
        for _, agent in ranked:
            if agent.id not in self._support_agents and len(selected) < self.max_domain_specialists:
                selected.append(agent)
        for support_id in self._support_agents:
            support = self.registry.get(support_id)
            if support is not None and all(item.id != support.id for item in selected):
                selected.append(support)

        outputs = await asyncio.gather(
            *(self._run_with_timeout(agent, cleaned) for agent in selected),
            return_exceptions=True,
        )
        team_results: list[dict[str, object]] = []
        for agent, output in zip(selected, outputs, strict=True):
            if isinstance(output, BaseException):
                failure = self._safe_failure(output)
                team_results.append({
                    "agent": {"id": agent.id, "name": agent.name},
                    **failure,
                })
            else:
                team_results.append({
                    "agent": {"id": agent.id, "name": agent.name},
                    "status": "completed",
                    "result": output,
                })

        successful = sum(item["status"] == "completed" for item in team_results)
        failed = len(team_results) - successful
        return {
            "status": "multi_agent_workflow" if failed == 0 else "multi_agent_partial_failure",
            "manager": self.name,
            "task": cleaned,
            "workflow_mode": "parallel_specialists_with_qa_and_delivery",
            "selected_agent": {"id": primary.id, "name": primary.name, "score": primary_score},
            "orchestration": {
                "selection_strategy": "highest positive capability scores, bounded to three domain specialists",
                "quality_review": "quality specialist included when registered",
                "delivery_handoff": "delivery specialist included when registered",
                "failure_policy": "Preserve successful outputs and identify failed or timed-out specialists for targeted retry.",
                "result_contract": "completed means the specialist returned a result; external actions require explicit tool-confirmed evidence.",
                "next_step": "Review outputs, retry only failed work, then authorize consequential external actions when appropriate.",
            },
            "team_count": len(team_results),
            "successful_agents": successful,
            "failed_agents": failed,
            "team_results": team_results,
            "note": "Specialists may return plans, checklists, or starter artifacts. External actions are not claimed unless a connected tool verifies them.",
        }


manager = MainManagerAgent()
