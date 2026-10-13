from fastapi.testclient import TestClient

from design_agent_hub.api import app
from design_agent_hub.connectors.canva import CanvaConnector
from design_agent_hub.figma_spec import FigmaSpecRequest, build_figma_spec

client = TestClient(app)


def test_health_is_available():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_canva_write_requires_explicit_approval(monkeypatch):
    monkeypatch.delenv("API_BEARER_TOKEN", raising=False)
    monkeypatch.setenv("APP_ENV", "development")
    response = client.post(
        "/connectors/canva/designs",
        json={"title": "Test design", "width": 1080, "height": 1080},
    )
    assert response.status_code == 409
    assert "user_approved" in response.json()["detail"]


def test_canva_create_validates_dimensions_before_network():
    import asyncio

    import pytest

    connector = CanvaConnector(token="")
    with pytest.raises(ValueError):
        asyncio.run(connector.create_design("invalid", 8000, 8000))


def test_canva_export_rejects_unsupported_format():
    import asyncio
    import pytest

    connector = CanvaConnector(token="")
    with pytest.raises(ValueError):
        asyncio.run(connector.start_export("design-id", "exe"))


def test_figma_spec_is_valid_plugin_payload():
    spec = build_figma_spec(FigmaSpecRequest(title="Test", headline="A headline"))
    assert len(spec["frames"]) == 1
    assert spec["frames"][0]["name"] == "Test"
    assert any(element["type"] == "text" for element in spec["frames"][0]["elements"])


def test_figma_spec_rejects_invalid_color():
    import pytest

    with pytest.raises(ValueError):
        FigmaSpecRequest(background="red")



def test_workflow_prepare_returns_plan_and_figma_spec(monkeypatch):
    monkeypatch.delenv("API_BEARER_TOKEN", raising=False)
    monkeypatch.setenv("APP_ENV", "development")
    response = client.post(
        "/workflow/prepare",
        json={
            "request": "Create a launch social post",
            "headline": "Launch day",
            "subheading": "A clear message for the audience.",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["execution_status"] == "plan_only"
    assert body["plan"]["steps"]
    assert body["figma_plugin_spec"]["frames"][0]["elements"]


def test_production_mode_requires_api_token(monkeypatch):
    monkeypatch.delenv("API_BEARER_TOKEN", raising=False)
    monkeypatch.setenv("APP_ENV", "production")
    response = client.get("/catalog")
    assert response.status_code == 503
    assert "API_BEARER_TOKEN" in response.json()["detail"]


def test_recommend_tools_endpoint_is_free_first_and_plan_only():
    response = client.post(
        "/tools/recommend",
        json={"task": "Create an Instagram post for a product launch"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["recommended_tool"] == "canva"
    assert body["execution_status"] == "recommendation_only"
