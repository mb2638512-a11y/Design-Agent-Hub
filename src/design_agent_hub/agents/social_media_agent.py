"""Social media specialist for multi-platform account operations and publishing plans."""

from __future__ import annotations

from typing import ClassVar


class SocialMediaSpecialistAgent:
    id = "social_media"
    name = "Social Media Agent"
    description = (
        "Plans multi-account social operations: channel setup, content calendars, publishing, "
        "moderation, analytics, and account-specific workflows with explicit approval boundaries."
    )
    capabilities: ClassVar[list[str]] = [
        "social media", "social-media", "social account", "social accounts", "social channel",
        "social channels", "manage my accounts", "manage accounts", "manage pages",
        "facebook page", "facebook pages", "instagram account", "youtube channel",
        "youtube channels", "tiktok account", "tiktok channels", "linkedin page",
        "pinterest account", "threads account", "publish posts", "schedule posts",
        "social scheduling", "social media manager", "social media management",
        "multi-platform", "multiple pages", "multiple channels", "community management",
        "engagement analytics", "social analytics", "content calendar for",
    ]
    platforms: ClassVar[tuple[str, ...]] = (
        "Facebook Pages", "Instagram", "YouTube", "TikTok", "LinkedIn Pages",
        "Pinterest", "Threads", "X",
    )

    def match_score(self, task: str) -> int:
        normalized = task.casefold()
        return sum(5 for capability in self.capabilities if capability in normalized)

    @staticmethod
    def _detect_platforms(task: str) -> list[str]:
        normalized = task.casefold()
        aliases = {
            "Facebook Pages": ("facebook", "fb page", "fb pages"),
            "Instagram": ("instagram", "insta", "ig account"),
            "YouTube": ("youtube", "shorts"),
            "TikTok": ("tiktok", "tik tok"),
            "LinkedIn Pages": ("linkedin",),
            "Pinterest": ("pinterest",),
            "Threads": ("threads",),
            "X": ("twitter", " x account", "x.com"),
        }
        return [
            platform for platform, aliases_for_platform in aliases.items()
            if any(alias in normalized for alias in aliases_for_platform)
        ]

    async def run(self, task: str) -> dict[str, object]:
        platforms = self._detect_platforms(task) or list(self.platforms)
        return {
            "agent_id": self.id,
            "agent_name": self.name,
            "result_type": "social_media_operations_plan",
            "execution_status": "plan_only_accounts_not_changed",
            "task": task,
            "target_platforms": platforms,
            "account_operations": [
                {"step": "Inventory", "actions": ["List each account/page/channel, owner, URL, audience, language, and current status.", "Identify duplicates, inactive channels, and account recovery needs."]},
                {"step": "Authorize", "actions": ["Connect each platform using its official OAuth flow or approved native integration.", "Request least-privilege scopes and store tokens in an encrypted secret store.", "Verify that the connected user is authorized to manage each account."]},
                {"step": "Setup", "actions": ["Prepare platform-specific profile names, bios, links, branding, and category details.", "Create pages/channels only where the official API permits it; otherwise guide the owner through the official UI.", "Require owner approval before creating, renaming, linking, or deleting accounts."]},
                {"step": "Content", "actions": ["Build a platform-adapted calendar with captions, creative briefs, hashtags, and format requirements.", "Run factual, brand, rights, accessibility, and platform-policy checks.", "Queue approved posts with timezone-aware schedules."]},
                {"step": "Publish", "actions": ["Publish only through authorized platform APIs or approved schedulers.", "Use an approval queue, retry limits, idempotency keys, and per-account rate limits.", "Record provider post IDs, URLs, timestamps, and failures."]},
                {"step": "Community", "actions": ["Monitor comments and inboxes only when permissions allow.", "Escalate sensitive, legal, safety, refund, and account-security issues to a human.", "Do not auto-spam, mass-follow, fake engagement, or bypass platform limits."]},
                {"step": "Analytics", "actions": ["Collect available reach, views, clicks, watch time, engagement, and conversion metrics.", "Compare results by platform and campaign, then recommend experiments.", "Respect platform retention rules and user privacy."]},
            ],
            "approval_gates": [
                "Explicit account-owner approval before creating or modifying pages/channels.",
                "Explicit approval before publishing, scheduling, messaging, deleting, or spending ad budget.",
                "Review all generated claims, affiliate disclosures, copyright, and brand assets before publication.",
            ],
            "integration_status": {
                "planning": "available",
                "live_account_access": "not_configured_by_this_agent",
                "automatic_page_creation": "platform_dependent_and_not_executed",
                "publishing_and_scheduling": "requires_authorized_platform_connectors",
                "analytics_and_moderation": "requires_authorized_scopes_and_connectors",
            },
            "next_steps_to_enable_end_to_end": [
                "Add encrypted per-user OAuth connections and token refresh/revocation.",
                "Implement one official connector at a time, starting with the user's priority platform.",
                "Add durable job queue, schedule/timezone handling, retries, audit logs, and rate limiting.",
                "Add an approval dashboard for posts and account changes.",
                "Run end-to-end tests against test accounts before enabling production writes.",
            ],
            "limitations": [
                "This agent currently creates an operations plan; it does not log into accounts, create pages, publish posts, or read analytics.",
                "Platform APIs differ: some account/page creation and messaging actions are unavailable or require app review/business eligibility.",
            ],
        }
