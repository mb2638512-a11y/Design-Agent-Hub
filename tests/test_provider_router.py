from design_agent_hub.provider_router import recommend_tools


def test_social_task_prefers_canva():
    result = recommend_tools("Create an Instagram post and social campaign graphic")
    assert result["recommended_tool"] == "canva"
    assert result["policy"].startswith("free_first")


def test_dashboard_task_prefers_penpot():
    result = recommend_tools("Design a responsive SaaS dashboard UI and prototype")
    assert result["recommended_tool"] == "penpot"


def test_figma_specific_request_is_routed():
    result = recommend_tools("Create a Figma wireframe and developer handoff")
    assert "figma" in [item["id"] for item in result["candidates"]]


def test_router_never_claims_connection_without_input():
    result = recommend_tools("Create a YouTube thumbnail")
    assert all(item["connection_status"] == "not_verified" for item in result["candidates"])
    assert result["execution_status"] == "recommendation_only"


def test_free_open_source_fallbacks_are_available():
    photo = recommend_tools("Retouch a product photo and remove the background")
    assert "gimp" in [item["id"] for item in photo["candidates"]]
    vector = recommend_tools("Create an SVG icon set and vector illustration")
    assert "inkscape" in [item["id"] for item in vector["candidates"]]
    three_d = recommend_tools("Make a 3D product render")
    assert "blender" in [item["id"] for item in three_d["candidates"]]
