from fastapi.testclient import TestClient

from design_agent_hub.api import app
from design_agent_hub.connectors.canva import CanvaConnector

client = TestClient(app)


def test_health_is_available():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_canva_write_requires_explicit_approval(monkeypatch):
    monkeypatch.delenv("API_BEARER_TOKEN", raising=False)
    response = client.post(
        "/connectors/canva/designs",
        json={"title": "Test design", "width": 1080, "height": 1080},
    )
    assert response.status_code == 409
    assert "user_approved" in response.json()["detail"]


def test_canva_create_validates_dimensions_before_network():
    connector = CanvaConnector(token="")
    import pytest
    with pytest.raises(ValueError):
        import asyncio
        asyncio.run(connector.create_design("invalid", 8000, 8000))


def test_canva_export_rejects_unsupported_format():
    connector = CanvaConnector(token="")
    import pytest
    with pytest.raises(ValueError):
        import asyncio
        asyncio.run(connector.start_export("design-id", "exe"))
