"""Capability and readiness catalog for supported social platforms.

This catalog describes integration targets, not live connection status. Actual writes
must use each provider's approved API, granted OAuth scopes, and user approval.
"""

from __future__ import annotations

from typing import Any


_PLATFORMS: tuple[dict[str, Any], ...] = (
    {
        "id": "facebook_pages",
        "name": "Facebook Pages",
        "account_types": ["Pages the user owns or is authorized to manage"],
        "workflow": ["profile_setup_checklist", "content_calendar", "publishing", "comments", "insights"],
        "connection": "Meta OAuth; Page permissions and app review may be required",
        "creation": "Create/claim pages through the official UI unless a currently approved API explicitly supports the requested operation",
        "status": "planned_not_connected",
        "docs": "https://developers.facebook.com/docs/graph-api/",
    },
    {
        "id": "instagram",
        "name": "Instagram",
        "account_types": ["Eligible Professional Business or Creator accounts"],
        "workflow": ["profile_setup_checklist", "content_calendar", "publishing", "comments", "insights"],
        "connection": "Meta OAuth; account type, linked assets, scopes, and app review can limit access",
        "creation": "Account creation and conversion may require the official Instagram app",
        "status": "planned_not_connected",
        "docs": "https://developers.facebook.com/docs/instagram-platform/",
    },
    {
        "id": "youtube",
        "name": "YouTube",
        "account_types": ["Channels the user owns or manages"],
        "workflow": ["channel_setup_checklist", "video_metadata", "upload", "comments", "analytics"],
        "connection": "Google OAuth; YouTube Data API and potentially Analytics API authorization",
        "creation": "Channel creation generally requires the owner to use the official YouTube UI",
        "status": "planned_not_connected",
        "docs": "https://developers.google.com/youtube/v3/docs",
    },
    {
        "id": "tiktok",
        "name": "TikTok",
        "account_types": ["TikTok accounts that authorize the app"],
        "workflow": ["profile_setup_checklist", "content_calendar", "approved_publishing", "available_metrics"],
        "connection": "TikTok for Developers OAuth; Content Posting scopes and app audit/approval may be required",
        "creation": "Account creation requires the official TikTok experience",
        "status": "planned_not_connected",
        "docs": "https://developers.tiktok.com/doc/content-posting-api-get-started",
    },
    {
        "id": "linkedin_pages",
        "name": "LinkedIn Pages",
        "account_types": ["Pages for which the user has sufficient admin permissions"],
        "workflow": ["page_setup_checklist", "content_calendar", "publishing", "available_analytics"],
        "connection": "LinkedIn OAuth; product access and organization permissions vary",
        "creation": "Page creation may require an eligible member to use LinkedIn's official UI",
        "status": "planned_not_connected",
        "docs": "https://learn.microsoft.com/linkedin/",
    },
    {
        "id": "pinterest",
        "name": "Pinterest",
        "account_types": ["Business or other eligible authorized accounts"],
        "workflow": ["profile_setup_checklist", "pin_calendar", "pin_publishing", "available_analytics"],
        "connection": "Pinterest OAuth; app access and granted scopes required",
        "creation": "Account creation and some business setup steps may require the official UI",
        "status": "planned_not_connected",
        "docs": "https://developers.pinterest.com/",
    },
    {
        "id": "threads",
        "name": "Threads",
        "account_types": ["Threads profiles that authorize the app"],
        "workflow": ["profile_setup_checklist", "content_calendar", "publishing", "available_insights"],
        "connection": "Threads API OAuth and approved publishing/insights scopes",
        "creation": "Profile creation requires the official Threads/Instagram experience",
        "status": "planned_not_connected",
        "docs": "https://developers.facebook.com/docs/threads/",
    },
    {
        "id": "x",
        "name": "X",
        "account_types": ["X accounts that authorize the app"],
        "workflow": ["profile_setup_checklist", "content_calendar", "publishing", "available_metrics"],
        "connection": "X developer app and OAuth; API tier, pricing, and endpoint access can vary",
        "creation": "Account creation requires the official X experience",
        "status": "planned_not_connected",
        "docs": "https://developer.x.com/en/docs",
    },
)


def list_social_platforms() -> dict[str, Any]:
    """Return a JSON-serializable catalog without secrets or implied live access."""
    return {
        "status": "catalog_only",
        "platform_count": len(_PLATFORMS),
        "live_connections_configured": False,
        "platforms": [dict(platform) for platform in _PLATFORMS],
        "shared_workflow": [
            "inventory_authorized_accounts",
            "official_oauth_and_least_privilege_scopes",
            "profile_and_brand_setup_checklist",
            "platform_adapted_content_and_creatives",
            "approval_queue",
            "durable_timezone_aware_scheduler",
            "authorized_publish_and_failure_reconciliation",
            "permitted_comment_and_inbox_triage",
            "available_analytics_and_reporting",
            "audit_logs_and_token_revocation",
        ],
        "safety": [
            "No passwords or access tokens in source code, logs, or chat.",
            "No publishing, messaging, deletion, or ad spend without explicit approval.",
            "No fake engagement, unsolicited bulk messaging, or platform-limit bypass.",
            "Only connect accounts the user owns or is authorized to manage.",
        ],
        "note": "This is a planning catalog. It does not mean provider integrations are connected or actions are executable.",
    }
