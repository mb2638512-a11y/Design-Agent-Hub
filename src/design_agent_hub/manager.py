"""Main manager agent and extensible specialist registry."""

from __future__ import annotations

from .agents.base import SpecialistAgent
from .agents.design_agent import DesignSpecialistAgent


class AgentRegistry:
    """Registry that lets future specialist agents be added without changing the manager."""

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

    def choose(self, task: str) -> SpecialistAgent | None:
        ranked = sorted(
            ((agent.match_score(task), agent) for agent in self._agents.values()),
            key=lambda pair: pair[0],
            reverse=True,
        )
        if not ranked or ranked[0][0] <= 0:
            return None
        return ranked[0][1]


class MainManagerAgent:
    """Orchestrates tasks by choosing and delegating to registered specialist agents."""

    id = "manager"
    name = "Main Manager Agent"

    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or AgentRegistry([DesignSpecialistAgent()])

    def status(self) -> dict[str, object]:
        return {
            "manager_id": self.id,
            "manager_name": self.name,
            "registered_agent_count": len(self.registry.list_agents()),
            "agents": self.registry.list_agents(),
        }

    async def dispatch(self, task: str) -> dict[str, object]:
        cleaned = task.strip()
        if len(cleaned) < 3:
            return {
                "status": "invalid_request",
                "manager": self.name,
                "message": "Task must contain at least 3 characters.",
            }
        agent = self.registry.choose(cleaned)
        if agent is None:
            return {
                "status": "no_matching_agent",
                "manager": self.name,
                "task": cleaned,
                "registered_agents": self.registry.list_agents(),
                "message": "No specialist currently matches this task. Register a suitable agent to extend coverage.",
            }
        result = await agent.run(cleaned)
        return {
            "status": "delegated",
            "manager": self.name,
            "task": cleaned,
            "selected_agent": {"id": agent.id, "name": agent.name},
            "result": result,
        }


manager = MainManagerAgent()
