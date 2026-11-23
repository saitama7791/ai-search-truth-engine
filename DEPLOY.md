# DEPLOY.md - deploying the Truth Engine

## Option A - GitHub Pages (zero-config)

Deploy-from-branch on `main`, root. The committed `index.html` is the site.
URL: https://saitama7791.github.io/ai-search-truth-engine/

## Option B - Cloudflare Pages (recommended for the final home)

Drag and drop (2 minutes, no terminal):
1. dash.cloudflare.com -> Workers & Pages -> Create -> Pages -> Upload assets
2. Project name: `ai-search-truth-engine`; upload this folder (must contain index.html)
3. Optional: Custom domain -> `truth-engine.aisearchos.com` (or attach to the main domain later)

Wrangler (terminal):

    npx wrangler pages deploy . --project-name=ai-search-truth-engine

Auto-deploy on every merge (set once):
1. Repo Settings -> Secrets and variables -> Actions -> add:
   - `CLOUDFLARE_API_TOKEN` (Cloudflare dashboard -> My Profile -> API Tokens -> token with Cloudflare Pages: Edit permission)
   - `CLOUDFLARE_ACCOUNT_ID` (dashboard right sidebar)
2. Done. `.github/workflows/cf-pages.yml` skips silently until the secrets exist; GitHub Pages keeps serving regardless.

## Option C - native page at aisearchos.com/truth-engine

The site is Astro. Simplest integration:
1. Copy `index.html` + `data/truth.json` into the site repo under `public/truth-engine/` (skip `favicon.svg`, the site already serves `/favicon.svg`).
2. Open `public/truth-engine/index.html` and delete the two Google Fonts `<link>` tags (`fonts.googleapis.com` / `fonts.gstatic.com`). The site self-hosts DM Sans under the same family name, and the site CSP (`font-src 'self' data:`) blocks external fonts anyway.
3. Optional polish: strip the cloned `<header>`/`<footer>` blocks and let the site layout wrap the `<main>`. The section markup and CSS variables are already native.
4. Add a nav or insights link: "Truth Engine" -> `/truth-engine`.

The robots.txt of aisearchos.com already allows GPTBot, OAI-SearchBot, ChatGPT-User, PerplexityBot, ClaudeBot, Google-Extended and Bingbot, so the board is fully crawlable on-domain.

## Data hygiene

- The dataset is public: `data/truth.json` (relative URL on the page) plus the raw file on GitHub.
- Cost per visitor: $0 (static files, no backend, no AI calls at runtime).
- Maintenance cost: one weekly agent sweep on free models; one human PR review.
