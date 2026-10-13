# Social Media Agent: all-platform implementation plan

## Goal

Build one owner-controlled workflow for Facebook Pages, Instagram, YouTube, TikTok, LinkedIn Pages, Pinterest, Threads, and X. The goal is end-to-end management of accounts the user owns or is authorized to manage, not a claim that every platform permits every action through its API.

## Current implementation

- The Social Media Agent routes social tasks and produces an operating plan.
- `GET /social/platforms` exposes a machine-readable capability/setup catalog for all eight platforms.
- No social account is connected by default. No credentials are bundled. This catalog is not a live connector and does not publish content.

## End-to-end target workflow

1. **Account inventory:** user links official accounts; record provider account IDs, ownership/admin status, supported actions, scopes, and token expiry. Never collect account passwords.
2. **Authorization:** use provider-specific OAuth, minimum scopes, state/PKCE where supported, CSRF protection, secure callback URLs, token refresh/revocation, and encrypted per-user token storage. Do not expose tokens to the browser or agent prompts.
3. **Brand workspace:** save brand voice, languages, audience, approved links, disclosures, brand assets and prohibited claims.
4. **Page/channel setup:** generate names, bios, profile/cover image briefs, links, categories, and setup checklists. Execute account creation only when the official API supports it and access is approved; otherwise guide the owner through the platform's official UI.
5. **Content studio:** generate platform-specific copy, image/video briefs, thumbnails, captions, alt text, subtitles, hashtags, and calls to action. Validate dimensions, media limits, rights, claims, and disclosures.
6. **Calendar and approvals:** timezone-aware calendar, per-account queues, draft/approve/reject controls, duplicate detection, and preview of the final platform-specific post.
7. **Publishing:** durable jobs, provider-specific adapters, idempotency keys, rate-limit handling, bounded retries, reconciliation for uncertain results, and storage of provider post IDs and URLs. Only publish after explicit approval unless the owner has separately configured a narrow policy for pre-approved content.
8. **Community operations:** read/reply only when the API and scopes allow it. Classify comments and route sensitive, legal, safety, account-security, refund, or high-impact messages to a human. Never mass-message unsolicited recipients.
9. **Analytics:** collect only metrics available to the authorized account; compare reach, views, watch time, clicks and engagement; explain missing metrics and provider delays.
10. **Reliability and governance:** per-tenant access controls, audit logs, retention limits, disconnect/revoke flow, webhook verification, monitoring, quota controls, backup/restore and incident response.

## Platform-specific constraints

| Platform | Integration direction | Important constraint |
|---|---|---|
| Facebook Pages | Meta Graph API | Page permissions, app review and eligible roles/scopes may be required. |
| Instagram | Instagram Platform / Graph API | Publishing and insights depend on eligible professional account types, linked assets and scopes. |
| YouTube | YouTube Data API plus Analytics API where needed | OAuth is needed for private data and writes; channel creation generally remains an owner UI step. |
| TikTok | Content Posting API | Publish scope and app audit/approval may be required; unaudited clients can have restricted visibility. |
| LinkedIn Pages | LinkedIn APIs | Product access and organization-admin permissions constrain publishing and analytics. |
| Pinterest | Pinterest API | OAuth, app access, endpoint permissions and quotas apply. |
| Threads | Threads API | OAuth and specific publishing/insights scopes apply; available features differ from Instagram. |
| X | X API | Endpoint access, quotas and pricing depend on the developer plan and current API access. |

Provider requirements change. Re-check each official developer document and current app approval before implementing a write endpoint. Do not hard-code a claim that every platform has identical scheduling, messaging, analytics, or account-creation support.

## Recommended delivery sequence

- **Phase 1 — foundation:** catalog (implemented), account connection model, OAuth security design, tenant isolation, audit event schema, approval state machine, and tests.
- **Phase 2 — first real adapter:** choose the first provider based on available developer access; implement OAuth callback, encrypted token vault, account inventory, and read-only profile verification.
- **Phase 3 — publishing:** add draft preview, explicit approval, upload/publish, provider result reconciliation, rate limiting, and sandbox/test-account coverage.
- **Phase 4 — remaining providers:** repeat adapter contract and conformance tests for all supported platforms; mark unsupported features explicitly.
- **Phase 5 — community and analytics:** add only endpoints and scopes that the app has been approved to use; add human escalation.
- **Phase 6 — production hardening:** encryption/key rotation, secrets redaction, per-user isolation, retention/deletion, abuse controls, observability, incident handling, and security review.

## Acceptance criteria before enabling real writes

- OAuth state validation and redirect URI allowlisting pass security tests.
- Tokens are encrypted at rest, never logged, and can be revoked/deleted.
- Every request is scoped to the authenticated user's linked accounts.
- Publishing requires a valid approval record and a deduplication key.
- Rate limits and provider errors cannot cause unbounded retries.
- Tests cover expired/revoked tokens, duplicate jobs, partial failures, permissions loss, and user disconnect.
- Production deployment is not enabled until each provider's current policy and app-review requirements are met.
