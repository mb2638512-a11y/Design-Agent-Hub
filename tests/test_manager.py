import pytest

from design_agent_hub.manager import AgentRegistry, MainManagerAgent


class FakeAgent:
    id = "fake"
    name = "Fake Agent"
    description = "Used to verify extensible registration."
    capabilities = ["fake tasks"]

    def match_score(self, task: str) -> int:
        return 10 if "fake task" in task.casefold() else 0

    async def run(self, task: str) -> dict[str, object]:
        return {"agent_id": self.id, "task": task, "execution_status": "test_only"}


def test_manager_registers_design_agent_by_default():
    manager = MainManagerAgent()
    status = manager.status()
    assert status["manager_id"] == "manager"
    assert status["registered_agent_count"] == 1
    assert status["agents"][0]["id"] == "design"


@pytest.mark.asyncio
async def test_manager_delegates_design_task():
    manager = MainManagerAgent()
    result = await manager.dispatch("Create an Instagram post design")
    assert result["status"] == "delegated"
    assert result["selected_agent"]["id"] == "design"
    assert result["result"]["result_type"] == "design_plan"


@pytest.mark.asyncio
async def test_manager_reports_when_no_agent_matches():
    manager = MainManagerAgent()
    result = await manager.dispatch("Calculate orbital trajectory")
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
