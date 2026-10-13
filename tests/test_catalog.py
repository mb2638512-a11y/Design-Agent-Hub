from design_agent_hub.catalog import get_catalog, search_catalog
from design_agent_hub.planner import PlanRequest, _fallback_plan


def test_catalog_has_categories_and_jobs():
    catalog = get_catalog()
    assert len(catalog) >= 12
    assert all(item["jobs"] for item in catalog)


def test_search_finds_youtube_thumbnail():
    results = search_catalog("YouTube thumbnail")
    assert results
    assert any("creator" in item["name"].lower() or "video" in item["name"].lower() for item in results)


def test_plan_is_plan_only_and_requires_confirmation():
    plan = _fallback_plan(PlanRequest(request="Create a YouTube thumbnail for a science channel"))
    assert plan.execution_status == "plan_only"
    assert plan.needs_user_confirmation_before_write is True
    assert plan.steps
