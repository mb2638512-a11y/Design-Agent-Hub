# Deploy Design Agent Hub for public use

The project is open source and can be used by anyone. This repository does not include a shared public API or shared secret. Each user, team, or community should deploy its own API and point the static web interface at that API.

## 1. Publish the web interface

The browser app is in `web/index.html`. It is static and can be hosted on GitHub Pages or any static web host. A GitHub Actions workflow in `.github/workflows/pages.yml` publishes the `web/` folder. In GitHub, open **Settings → Pages** and select **GitHub Actions** as the build/deployment source if required.

## 2. Deploy your own API on Render

1. Fork this repository to your own GitHub account.
2. In Render, create a new Blueprint and select your fork. Render reads `render.yaml`.
3. Wait for deployment and copy the service URL.
4. Set `CORS_ORIGINS` to the exact origin hosting your frontend. Example: `https://YOUR-USERNAME.github.io` (no path and no trailing slash). If you host the UI elsewhere, use that origin instead.
5. Render generates `API_BEARER_TOKEN`. Keep it private. Enter it in the web UI only when using your own API.
6. Check `https://YOUR-API-URL/health` and open `https://YOUR-API-URL/docs` to verify the service.

Free hosting plans may sleep, limit resources, or change. Check the provider's current pricing and limits before relying on it.

## 3. Run with Docker

```bash
docker build -t design-agent-hub .
docker run --rm -p 8000:8000 \
  -e APP_ENV=production \
  -e API_BEARER_TOKEN='replace-with-a-long-random-secret' \
  -e CORS_ORIGINS='https://YOUR-USERNAME.github.io' \
  design-agent-hub
```

Use HTTPS behind a reverse proxy in production. Keep secrets in the hosting platform's secret manager, rotate them, and restrict CORS to the frontend origin you actually use. Do not expose an unauthenticated API to the public internet.

## 4. Use the web interface

1. Open the static site.
2. Enter your deployed API URL and private API bearer token.
3. Click **Check connection**.
4. Enter a task and choose **Run on my API**. You can also download editable SVG/HTML starter assets or a ZIP starter package.

The UI keeps the token in page memory only and does not save it in localStorage. Clear the fields after use, especially on a shared device. The **Try demo mode** button is local-only sample output; it does not call an AI model or contact social platforms.

## Current limits

- Agents return plans and starter content; they do not guarantee arbitrary tasks are completed autonomously.
- The social platform catalog is informational. OAuth, account inventory, scheduling, publishing, comments, and analytics adapters still need implementation and provider approval.
- Never enter provider passwords or OAuth client secrets in prompts or source control. Public writes and sensitive actions should require explicit approval.
