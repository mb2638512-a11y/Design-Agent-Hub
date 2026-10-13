"""Tests for planner model failover and deterministic safety contracts."""

import asyncio

from design_agent_hub import planner


def test_planner_tries_fallback_model_after_primary_failure(monkeypatch):
    configs = {
        "MODEL": ("https://primary.example/v1", "primary-key", "primary-model"),
        "MODEL_FALLBACK": ("https://fallback.example/v1", "fallback-key", "fallback-model"),
    }
    monkeypatch.setattr(planner, "_model_config", lambda prefix="MODEL": configs.get(prefix))
    calls = []

    async def fake_request(req, config):
        calls.append(config)
        if config == configs["MODEL"]:
            raise RuntimeError("provider unavailable")
        return planner.DesignPlan(
            summary="fallback plan",
            matched_categories=["Product UI/UX"],
            steps=["Plan safely"],
            suggested_tools=["Design Agent Hub"],
            required_inputs=[],
            quality_checks=["Review before use"],
        )

    monkeypatch.setattr(planner, "_request_model", fake_request)
    result = asyncio.run(planner.create_plan(planner.PlanRequest(request="Create a product landing page")))
    assert calls == [configs["MODEL"], configs["MODEL_FALLBACK"]]
    assert result.summary == "fallback plan"
    assert result.execution_status == "plan_only"
    assert result.needs_user_confirmation_before_write is True


def test_planner_uses_deterministic_fallback_when_no_models_configured(monkeypatch):
    monkeypatch.setattr(planner, "_model_config", lambda prefix="MODEL": None)
    result = asyncio.run(planner.create_plan(planner.PlanRequest(request="Create a product landing page")))
    assert result.execution_status == "plan_only"
    assert result.steps
