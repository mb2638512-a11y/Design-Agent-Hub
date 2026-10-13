"""Main manager agent, specialist registry, and bounded multi-agent orchestration."""

from __future__ import annotations

import asyncio

from .agents.base import SpecialistAgent
from .agents.coding_agent import CodingSpecialistAgent
from .agents.delivery_agent import DeliverySpecialistAgent
from .agents.design_agent import DesignSpecialistAgent
from .agents.quality_agent import QualitySpecialistAgent
from .agents.research_agent import ResearchSpecialistAgent


class AgentRegistry:
    """Registry that lets specialists be added without changing the dispatcher."""

    def __init__(self, agents: list[SpecialistAgent] | None = None) -> None:
        self._agents: dict[str, SpecialistAgent] = {}
        for agent in agents or []:
            self.register(agent)

    def register(self, agent: SpecialistAgent) -> None:
        if not agent.id.strip():
            raise ValueError("Agent id must not be empty")
        if agent.id in self._agents:
            raise ValueError(f"Agent already registered: {agent.id}")
        self._agents[agent.id] = agent

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
        """Return matching specialists from highest to lowest score."""
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
    """Routes simple tasks and coordinates specialists for complex requests."""

    id = "manager"
    name = "Main Manager Agent"
    _complex_markers = (
        "end-to-end", "end to end", "complete package", "full project",
        "from start to finish", "launch the whole", "entire workflow",
    )
    _support_agents = ("quality", "delivery")

    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or AgentRegistry(
            [
                DesignSpecialistAgent(),
                CodingSpecialistAgent(),
                ResearchSpecialistAgent(),
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
            "routing_mode": "capability_keyword_scoring",
            "multi_agent_workflows": True,
        }

    async def dispatch(self, task: str) -> dict[str, object]:
        cleaned = task.strip()
        if len(cleaned) < 3:
            return {
                "status": "invalid_request",
                "manager": self.name,
                "message": "Task must contain at least 3 characters.",
            }

        ranked = [(score, agent) for score, agent in self.registry.rank(cleaned) if score > 0]
        if not ranked:
            return {
                "status": "no_matching_agent",
                "manager": self.name,
                "task": cleaned,
                "registered_agents": self.registry.list_agents(),
                "message": "No specialist currently matches this task. Register a suitable agent to extend coverage.",
            }

        primary_score, primary = ranked[0]
        domain_matches = [
            agent for score, agent in ranked
            if agent.id not in self._support_agents and score > 0
        ]
        normalized = cleaned.casefold()
        complex_task = (
            any(marker in normalized for marker in self._complex_markers)
            or len(domain_matches) >= 2
        )
        if not complex_task:
            result = await primary.run(cleaned)
            return {
                "status": "delegated",
                "manager": self.name,
                "task": cleaned,
                "selected_agent": {"id": primary.id, "name": primary.name, "score": primary_score},
                "workflow_mode": "single_specialist",
                "result": result,
            }

        # Keep orchestration bounded: at most three domain specialists plus QA and delivery.
        selected: list[SpecialistAgent] = []
        for _, agent in ranked:
            if agent.id not in self._support_agents and len(selected) < 3:
                selected.append(agent)
        for support_id in self._support_agents:
            support = self.registry.get(support_id)
            if support is not None and all(item.id != support.id for item in selected):
                selected.append(support)

        outputs = await asyncio.gather(*(agent.run(cleaned) for agent in selected))
        team_results = [
            {"agent": {"id": agent.id, "name": agent.name}, "result": output}
            for agent, output in zip(selected, outputs, strict=True)
        ]
        return {
            "status": "multi_agent_workflow",
            "manager": self.name,
            "task": cleaned,
            "workflow_mode": "parallel_specialists_with_qa_and_delivery",
            "selected_agent": {"id": primary.id, "name": primary.name, "score": primary_score},
            "team_count": len(team_results),
            "team_results": team_results,
            "note": "Specialists currently return plans, checklists, or starter content. This is not proof that external tools ran or files were published.",
        }


manager = MainManagerAgent()
