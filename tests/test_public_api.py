from fastapi.testclient import TestClient

from design_agent_hub.api import app


def test_health_is_public_for_deployment_health_checks():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_social_platform_catalog_endpoint_is_available_in_development():
    response = TestClient(app).get("/social/platforms")
    assert response.status_code == 200
    assert response.json()["platform_count"] == 8


def test_cors_preflight_allows_configured_local_frontend():
    response = TestClient(app).options(
        "/manager/dispatch",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
