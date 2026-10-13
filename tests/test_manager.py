"""Tests for the manager and extensible agent registry."""

import asyncio
from typing import ClassVar

import pytest

from design_agent_hub.manager import AgentRegistry, MainManagerAgent


class FakeAgent:
    id = "fake"
    name = "Fake Agent"
    description = "Used to verify extensible registration."
    capabilities: ClassVar[list[str]] = ["fake tasks"]

    def match_score(self, task: str) -> int:
        return 10 if "fake task" in task.casefold() else 0

    async def run(self, task: str) -> dict[str, object]:
        return {"agent_id": self.id, "task": task, "execution_status": "test_only"}


class SlowAgent(FakeAgent):
    id = "slow"
    name = "Slow Agent"

    async def run(self, task: str) -> dict[str, object]:
        await asyncio.sleep(0.05)
        return {"agent_id": self.id, "task": task}


def test_manager_registers_specialists_by_default():
    manager = MainManagerAgent()
    status = manager.status()
    assert status["manager_id"] == "manager"
    assert status["registered_agent_count"] == 7
    assert {item["id"] for item in status["agents"]} == {
        "design", "coding", "content", "research", "social_media", "quality", "delivery"
    }
    assert status["execution_limits"]["agent_timeout_seconds"] > 0


def test_manager_delegates_design_task():
    manager = MainManagerAgent()
    result = asyncio.run(manager.dispatch("Create an Instagram post design"))
    assert result["status"] == "delegated"
    assert result["selected_agent"]["id"] == "design"
    assert result["result"]["result_type"] == "design_plan"
    assert result["result"]["starter_asset"]["format"] == "svg"


def test_manager_routes_coding_task():
    result = asyncio.run(MainManagerAgent().dispatch("Debug a Python API bug"))
    assert result["status"] == "delegated"
    assert result["selected_agent"]["id"] == "coding"
    assert result["result"]["result_type"] == "implementation_plan"


def test_manager_runs_collaborative_workflow_for_cross_domain_request():
    result = asyncio.run(
        MainManagerAgent().dispatch(
            "Research competitors, build a website, test accessibility, and deliver the complete package"
        )
    )
    assert result["status"] == "multi_agent_workflow"
    ids = {item["agent"]["id"] for item in result["team_results"]}
    assert "research" in ids
    assert "coding" in ids
    assert "quality" in ids
    assert "delivery" in ids


def test_manager_reports_when_no_agent_matches():
    result = asyncio.run(MainManagerAgent().dispatch("Calculate orbital trajectory"))
    assert result["status"] == "no_matching_agent"


def test_registry_can_accept_future_agents():
    registry = AgentRegistry()
    registry.register(FakeAgent())
    assert registry.choose("Handle fake task") is not None
    assert registry.list_agents()[0]["id"] == "fake"


def test_registry_rejects_duplicate_agent_ids():
    registry = AgentRegistry([FakeAgent()])
    with pytest.raises(ValueError, match="already registered"):
        registry.register(FakeAgent())


def test_manager_routes_content_request():
    result = asyncio.run(MainManagerAgent().dispatch("Write a YouTube script for a product launch"))
    assert result["status"] == "delegated"
    assert result["selected_agent"]["id"] == "content"
    assert result["result"]["result_type"] == "content_starter_pack"


def test_manager_returns_html_starter_for_landing_page():
    result = asyncio.run(MainManagerAgent().dispatch("Create a landing page website"))
    assert result["status"] == "delegated"
    asset = result["result"]["starter_asset"]
    assert asset["format"] == "html"
    assert "<!doctype html>" in asset["content"].lower()
    assert "viewport" in asset["content"]


def test_manager_routes_social_media_account_workflow():
    task = "Manage my social media accounts across Facebook Pages and YouTube channels end-to-end"
    result = asyncio.run(MainManagerAgent().dispatch(task))
    assert result["status"] == "multi_agent_workflow"
    assert result["selected_agent"]["id"] == "social_media"
    social_result = next(item["result"] for item in result["team_results"] if item["agent"]["id"] == "social_media")
    assert social_result["result_type"] == "social_media_operations_plan"
    assert social_result["execution_status"] == "plan_only_accounts_not_changed"
    assert "Facebook Pages" in social_result["target_platforms"]
    assert "YouTube" in social_result["target_platforms"]
    assert social_result["approval_gates"]


def test_manager_collapses_excess_whitespace_before_dispatch():
    result = asyncio.run(MainManagerAgent().dispatch("  Debug   a Python API bug  "))
    assert result["status"] == "delegated"
    assert result["task"] == "Debug a Python API bug"
    assert result["result"]["task"] == "Debug a Python API bug"


def test_manager_rejects_oversized_task():
    result = asyncio.run(MainManagerAgent().dispatch("x" * 20_001))
    assert result["status"] == "task_too_large"
    assert result["max_task_characters"] == 20_000


def test_manager_reports_specialist_timeout_without_hanging():
    manager = MainManagerAgent(AgentRegistry([SlowAgent()]))
    manager.agent_timeout_seconds = 0.001
    result = asyncio.run(manager.dispatch("Handle a fake task"))
    assert result["status"] == "agent_timed_out"
    assert result["failure"]["status"] == "timed_out"
    assert result["selected_agent"]["id"] == "slow"
