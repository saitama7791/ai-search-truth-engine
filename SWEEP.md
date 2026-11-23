# SWEEP.md - the weekly sweep process

This is the documented process the automation agent follows every week, and the contract the human reviewer can hold it to. Preview: https://saitama7791.github.io/ai-search-truth-engine/ - intended home: https://aisearchos.com/truth-engine

## The weekly loop (every sweep)

1. `git pull` latest main.
2. Research what changed in AI search since the last sweep. Official sources first:
   - Google crawling changelog: https://developers.google.com/crawling/docs/changelog
   - Google user-triggered fetchers: https://developers.google.com/crawling/docs/crawlers-fetchers/google-user-triggered-fetchers
   - OpenAI bots: https://platform.openai.com/docs/bots
   - Perplexity crawlers: https://docs.perplexity.ai/docs/resources/perplexity-crawlers
   - Anthropic robots: https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler
   - Bing: https://blogs.bing.com/webmaster/ and https://www.bing.com/webmasters

   Then reputable analysis: Ahrefs blog, Semrush, Search Engine Land, Search Engine Journal, SparkToro, The Verge, arXiv GEO/AEO research.

3. Update `data/truth.json` ONLY (never edit index.html, page.tmpl.html or scripts/):
   - bump `sweep_id` (+1) and set `sweep_date` to today (YYYY-MM-DD)
   - rewrite `sweep_note` as one honest sentence about what this sweep did
   - add dated entries to `updates` (each MUST carry a real source URL you actually saw; impact: high|medium|low)
   - update `platforms` (current_model / crawlers / field_notes) when docs changed, with sources added
   - add or change `tactics` verdicts ONLY with published evidence; set last_verified to today
   - link-check at least 5 older entries per sweep; fix or prune rot
   - prune `updates` entries older than 12 months

4. Rebuild: `python3 scripts/validate.py && python3 scripts/build.py` - both must pass. Commit the regenerated index.html together with truth.json.

5. NEVER push to main. Branch: `sweep/YYYY-MM-DD`. Commit message: `sweep: YYYY-MM-DD <summary>`.

6. Open a pull request:
   - title: `Sweep YYYY-MM-DD: <one-line summary>`
   - body: bullet list of every change with its source URL; a "verdicts changed" section if any

7. Report the PR URL and stop. A human (Ankit) reviews and merges. Merge auto-deploys (GitHub Pages; Cloudflare Pages too if repo secrets are set).

## Hard rules

- Every claim MUST have a URL you actually saw in search results this sweep. If you did not see it, it is not evidence.
- No fabricated or guessed URLs. No vibes.
- Verdicts enum: `working | mixed | conditional | not-working | myth`. per_platform verdicts may also use `no-effect`.
- Platform ids: `chatgpt | google-ai | perplexity | claude | copilot`.
- If validate.py fails, fix the data - never the validator.
- If nothing material changed, still open the PR with just - the sweep_date bump and a "no material changes" note (proves the sweep ran).
- Never merge your own PR. Never force-push.
- Cost discipline: run on free/cheap models; no paid data sources.
