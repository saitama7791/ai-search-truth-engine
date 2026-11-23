# AI Search Truth Engine

A free, evidence-backed board of what actually works in AI search — every verdict carries its source and date. Built for [aisearchos.com](https://aisearchos.com) (AI Search OS), designed for B2B industrial software and manufacturing sellers.

**Live preview:** https://saitama7791.github.io/ai-search-truth-engine/
**Intended home:** https://aisearchos.com/truth-engine

## How it works

- `data/truth.json` — the living dataset. The single source of truth. **This is the only file sweeps edit.**
- `scripts/build.py` — deterministic renderer: `page.tmpl.html` + `data/truth.json` + `scripts/app.js` → `index.html` (self-contained, zero dependencies, zero AI cost per visitor).
- `scripts/validate.py` — dataset gate: unique ids, verdict enums, https source URLs, ISO dates. Build refuses to run on invalid data.
- The full board is server-rendered into the HTML (readable by crawlers that never run JS); the dataset is also embedded as JSON for the interactive layer (search, verdict/platform filters, copy-snapshot).
- `index.html` is committed, so GitHub Pages deploy-from-branch serves it with zero build steps.

## The self-improvement loop

A weekly agent sweep (see `AGENTS.md`) researches platform changes from official sources, updates `data/truth.json`, revalidates, rebuilds, and opens a pull request. A human approves every PR. Merge → auto-deploy.

## Local development

```bash
python3 scripts/validate.py      # validate dataset
python3 scripts/build.py          # render index.html
python3 -m http.server 8901      # serve at http://127.0.0.1:8901
```

## Deployment

See [DEPLOY.md](DEPLOY.md) — GitHub Pages (zero-config), Cloudflare Pages (wrangler or dashboard), or embedding87economics (GitHub Pages, Cloudflare, or drop (including integration into the Astro site at aisearchos.com/truth-engine).

## Design

security-note: The design token system, typography and components replicate aisearchos.com so the tool reads as native. Content and brand belong to AI Search OS.
