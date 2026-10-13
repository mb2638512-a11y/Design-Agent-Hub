"""Tests for the social platform capability catalog."""

from design_agent_hub.social_platforms import list_social_platforms


def test_social_catalog_covers_all_requested_platforms():
    catalog = list_social_platforms()
    assert catalog["platform_count"] == 8
    assert {item["id"] for item in catalog["platforms"]} == {
        "facebook_pages", "instagram", "youtube", "tiktok",
        "linkedin_pages", "pinterest", "threads", "x",
    }


def test_social_catalog_never_claims_live_connections():
    catalog = list_social_platforms()
    assert catalog["status"] == "catalog_only"
    assert catalog["live_connections_configured"] is False
    assert all(item["status"] == "planned_not_connected" for item in catalog["platforms"])
    assert any("approval" in item for item in catalog["safety"])
