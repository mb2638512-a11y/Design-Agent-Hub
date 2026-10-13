# Security Policy

## Supported versions
The latest code on the default branch is the only version currently considered for security fixes.

## Reporting a vulnerability
Please do not publish access tokens, private design files, or exploit details in public issues. Contact the repository owner privately through GitHub's security reporting feature if enabled, or ask for a private reporting channel before sharing sensitive details.

## Credential hygiene
- Never commit `.env`, access tokens, OAuth secrets, customer content, or exported private designs.
- Revoke and rotate any credential that may have been exposed.
- Use least-privilege scopes and keep this service bound to localhost until authentication, rate limiting, and deployment hardening are complete.
