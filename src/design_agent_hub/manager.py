"""Main manager agent, specialist registry, and bounded multi-agent orchestration."""

from __future__ import annotations

import asyncio
import json

from .agents.base import SpecialistAgent
from .agents.coding_agent import CodingSpecialistAgent
from .agents.content_agent import ContentSpecialistAgent
from .agents.delivery_agent import DeliverySpecialistAgent
from .agents.design_agent import DesignSpecialistAgent
from .agents.quality_agent import QualitySpecialistAgent
from .agents.research_agent import ResearchSpecialistAgent
from .agents.social_media_agent import SocialMediaSpecialistAgent
from .task_memory import remember_task


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
            {"id": agent.id, "name": agent.name, "description": agent.description, "capabilities": list(agent.capabilities)}
            for agent in self._agents.values()
        ]

    def rank(self, task: str) -> list[tuple[int, SpecialistAgent]]:
        """Rank by capability score; stable sorting makes ties deterministic."""
        return sorted(((agent.match_score(task), agent) for agent in self._agents.values()), key=lambda pair: pair[0], reverse=True)

    def choose(self, task: str) -> SpecialistAgent | None:
        ranked = self.rank(task)
        return ranked[0][1] if ranked and ranked[0][0] > 0 else None

    def get(self, agent_id: str) -> SpecialistAgent | None:
        return self._agents.get(agent_id)


class MainManagerAgent:
    """Plan, route, bound, validate, and report specialist workflows."""

    id = "manager"
    name = "Main Manager Agent"
    agent_timeout_seconds = 60
    max_task_characters = 20_000
    max_domain_specialists = 3
    _complex_markers = (
        "end-to-end", "end to end", "complete package", "full project", "from start to finish",
        "launch the whole", "entire workflow", "automate", "across all", "manage everything",
        "whole campaign", "research and create", "design and build", "create and publish",
        "plan and execute", "audit and fix", "build and test",
    )
    _multi_step_markers = (",", ";", " and ", " then ", " followed by ")
    _support_agents = ("quality", "delivery")

    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or AgentRegistry([
            DesignSpecialistAgent(), CodingSpecialistAgent(), ContentSpecialistAgent(),
            ResearchSpecialistAgent(), SocialMediaSpecialistAgent(), QualitySpecialistAgent(),
            DeliverySpecialistAgent(),
        ])

    def status(self) -> dict[str, object]:
        agents = self.registry.list_agents()
        return {
            "manager_id": self.id,
            "manager_name": self.name,
            "registered_agent_count": len(agents),
            "agents": agents,
            "routing_mode": "capability_scoring_with_bounded_collaboration",
            "planning": "deterministic_task_plan_with_specialist_assignments",
            "output_validation": "structure_and_json_serializability_checks",
            "memory": "opt_in_local_sqlite_task_summaries",
            "model_failover": "primary_openai_compatible_then_optional_fallback_then_deterministic_planner",
            "execution_limits": {"max_task_characters": self.max_task_characters, "agent_timeout_seconds": self.agent_timeout_seconds, "max_domain_specialists": self.max_domain_specialists},
            "multi_agent_workflows": True,
            "operating_principles": [
                "Complete safe, useful parts instead of refusing an entire mixed request unnecessarily.",
                "Route focused tasks to the strongest matching specialist; collaborate for multi-step or cross-domain work.",
                "Use bounded execution so one stalled specialist cannot block the whole workflow indefinitely.",
                "Validate returned structure and preserve successful outputs when another specialist fails.",
                "Distinguish plans and generated artifacts from external actions verified by connected tools.",
                "Require authorization for consequential external writes, publication, deletion, messaging, or spending.",
                "Persist task summaries only when local memory is explicitly enabled.",
            ],
        }

    def build_task_plan(self, task: str, ranked: list[tuple[int, SpecialistAgent]]) -> dict[str, object]:
        """Build a transparent execution plan before running agents."""
        is_complex = any(marker in task.casefold() for marker in self._complex_markers) or (
            len([agent for score, agent in ranked if score > 0 and agent.id not in self._support_agents]) >= 2
            and any(marker in f" {task.casefold()} " for marker in self._multi_step_markers)
        )
        domains = [
            {"agent_id": agent.id, "agent_name": agent.name, "capability_score": score, "assignment": agent.description}
            for score, agent in ranked
            if score > 0 and agent.id not in self._support_agents
        ][: self.max_domain_specialists if is_complex else 1]
        if is_complex:
            for support_id in self._support_agents:
                support = self.registry.get(support_id)
                if support:
                    domains.append({"agent_id": support.id, "agent_name": support.name, "capability_score": 0, "assignment": support.description})
        return {
            "mode": "multi_agent" if is_complex else "single_specialist",
            "goal": task,
            "steps": [
                {"step": 1, "action": "Select specialists by capability score", "status": "planned"},
                {"step": 2, "action": "Execute within per-agent timeout", "status": "pending"},
                {"step": 3, "action": "Validate result structure and preserve partial successes", "status": "pending"},
                {"step": 4, "action": "Return deliverables, limitations, and next actions", "status": "pending"},
            ],
            "assignments": domains,
            "external_actions_authorized": False,
        }

    async def _run_with_timeout(self, agent: SpecialistAgent, task: str) -> dict[str, object]:
        return await asyncio.wait_for(agent.run(task), timeout=self.agent_timeout_seconds)

    @staticmethod
    def _safe_failure(exc: BaseException) -> dict[str, object]:
        if isinstance(exc, (TimeoutError, asyncio.TimeoutError)):
            return {"status": "timed_out", "error": "Specialist exceeded the manager execution time limit."}
        return {"status": "failed", "error": f"{type(exc).__name__}: specialist failed; inspect server logs for details."}

    @staticmethod
    def _validate_output(output: object) -> dict[str, object]:
        """Check basic output integrity; this is not a claim of semantic correctness."""
        issues: list[str] = []
        if not isinstance(output, dict):
            return {"valid": False, "issues": ["Specialist result must be a dictionary/object."]}
        if not output:
            issues.append("Specialist returned an empty object.")
        try:
            json.dumps(output, ensure_ascii=False)
        except (TypeError, ValueError):
            issues.append("Specialist output is not JSON serializable.")
        if not output.get("agent_id"):
            issues.append("Result does not identify its originating agent.")
        return {"valid": not issues, "issues": issues, "scope": "structural_only_not_semantic_review"}

    def _remember(self, task: str, result: dict[str, object]) -> dict[str, object]:
        try:
            return remember_task(task, result)
        except Exception as exc:  # noqa: BLE001 - memory must never take down task execution
            return {"enabled": True, "stored": False, "reason": f"memory_unavailable:{type(exc).__name__}"}

    @staticmethod
    def _repair_output(agent: SpecialistAgent, output: object) -> tuple[object, dict[str, object]]:
        """Apply a minimal safe repair to structurally incomplete object results."""
        validation = MainManagerAgent._validate_output(output)
        if validation["valid"] or not isinstance(output, dict):
            return output, validation
        repaired = dict(output)
        changes: list[str] = []
        if not repaired.get("agent_id"):
            repaired["agent_id"] = agent.id
            changes.append("added_missing_agent_id")
        if not repaired.get("agent_name"):
            repaired["agent_name"] = agent.name
            changes.append("added_missing_agent_name")
        if changes:
            repaired["manager_repair"] = {"applied": True, "changes": changes, "note": "Metadata repair only; content correctness is not guaranteed."}
        validation = MainManagerAgent._validate_output(repaired)
        if changes:
            validation["repair"] = {"applied": True, "changes": changes}
        return repaired, validation

    async def dispatch(self, task: str) -> dict[str, object]:
        cleaned = " ".join(task.split()) if isinstance(task, str) else ""
        if len(cleaned) < 3:
            return {"status": "invalid_request", "manager": self.name, "message": "Task must contain at least 3 non-whitespace characters."}
        if len(cleaned) > self.max_task_characters:
            return {"status": "task_too_large", "manager": self.name, "max_task_characters": self.max_task_characters, "message": "Split this request into smaller tasks so specialists can process it reliably."}

        ranked = [(score, agent) for score, agent in self.registry.rank(cleaned) if score > 0]
        if not ranked:
            return {"status": "no_matching_agent", "manager": self.name, "task": cleaned, "registered_agents": self.registry.list_agents(), "message": "No specialist currently matches this task. Try describing the desired outcome and domain, or register a suitable specialist."}

        primary_score, primary = ranked[0]
        plan = self.build_task_plan(cleaned, ranked)
        if plan["mode"] == "single_specialist":
            try:
                result = await self._run_with_timeout(primary, cleaned)
            except BaseException as exc:
                if isinstance(exc, (KeyboardInterrupt, SystemExit, asyncio.CancelledError)):
                    raise
                failure = self._safe_failure(exc)
                return {"status": "agent_failed" if failure["status"] == "failed" else "agent_timed_out", "manager": self.name, "task": cleaned, "selected_agent": {"id": primary.id, "name": primary.name, "score": primary_score}, "failure": failure, "retry_guidance": "Retry once, simplify the task, or use a different specialist if the problem persists."}
            result, validation = self._repair_output(primary, result)
            response: dict[str, object] = {
                "status": "delegated" if validation["valid"] else "agent_invalid_output",
                "manager": self.name,
                "task": cleaned,
                "selected_agent": {"id": primary.id, "name": primary.name, "score": primary_score},
                "workflow_mode": "single_specialist",
                "task_plan": plan,
                "quality_gate": validation,
                "result_contract": "A returned result is not proof of an external action unless a connected tool confirms it.",
                "result": result,
            }
            response["memory"] = self._remember(cleaned, response)
            return response

        selected: list[SpecialistAgent] = []
        for _, agent in ranked:
            if agent.id not in self._support_agents and len(selected) < self.max_domain_specialists:
                selected.append(agent)
        for support_id in self._support_agents:
            support = self.registry.get(support_id)
            if support is not None and all(item.id != support.id for item in selected):
                selected.append(support)

        outputs = await asyncio.gather(*(self._run_with_timeout(agent, cleaned) for agent in selected), return_exceptions=True)
        team_results: list[dict[str, object]] = []
        for agent, output in zip(selected, outputs, strict=True):
            if isinstance(output, BaseException):
                team_results.append({"agent": {"id": agent.id, "name": agent.name}, **self._safe_failure(output)})
                continue
            output, validation = self._repair_output(agent, output)
            team_results.append({"agent": {"id": agent.id, "name": agent.name}, "status": "completed" if validation["valid"] else "invalid_output", "quality_gate": validation, "result": output})

        successful = sum(item["status"] == "completed" for item in team_results)
        failed = len(team_results) - successful
        response = {
            "status": "multi_agent_workflow" if failed == 0 else "multi_agent_partial_failure",
            "manager": self.name,
            "task": cleaned,
            "workflow_mode": "parallel_specialists_with_qa_and_delivery",
            "selected_agent": {"id": primary.id, "name": primary.name, "score": primary_score},
            "task_plan": plan,
            "orchestration": {
                "selection_strategy": "highest positive capability scores, bounded to three domain specialists",
                "quality_review": "quality specialist included when registered; structural validation runs on every result",
                "delivery_handoff": "delivery specialist included when registered",
                "failure_policy": "Preserve successful outputs and identify failed or invalid results for targeted retry; automatic retries are avoided for safety.",
                "result_contract": "completed means a structurally valid result was returned; external actions require explicit tool-confirmed evidence.",
                "next_step": "Review outputs, retry only failed work, then authorize consequential external actions when appropriate.",
            },
            "team_count": len(team_results),
            "successful_agents": successful,
            "failed_agents": failed,
            "team_results": team_results,
            "note": "Structural checks do not prove factual accuracy or design quality. Specialists may return plans or starter artifacts; external actions require tool verification.",
        }
        response["memory"] = self._remember(cleaned, response)
        return response


manager = MainManagerAgent()
