---
name: search-tool-fallback
description: When mcp_minimax_plan_web_search fails (404), fall back to mcp_searxng_search. Always try MiniMax first, switch to SearXNG on any error.
triggers:
  - search returns 404
  - mcp_minimax_plan_web_search error
  - cron research task
---

# Search Tool Fallback — MiniMax → SearXNG

## Context

The `mcp_minimax_plan_web_search` (MiniMax Coding Plan MCP) endpoint at `api.minimaxi.com/v1/v1/coding_plan/search` consistently returns `404 Client Error: 404 Page not found`. This is a persistent endpoint issue, not transient — retrying will not help.

## Fallback Chain

1. **Primary**: `mcp_minimax_plan_web_search` — try first
2. **Fallback**: `mcp_searxng_search` with `engines: "google"` — use immediately when MiniMax fails or returns 404

## Usage Pattern

```
# Correct: try MiniMax, if any error → switch to SearXNG
mcp_minimax_plan_web_search(query="...")
# if result is 404 or empty → immediately call:
mcp_searxng_search(query="...", engines="google")
```

## Important Gotchas

- **Never retry MiniMax twice** in a loop — it consistently fails on this endpoint
- **Don't check MiniMax results first** then fallback conditionally — just call SearXNG on any exception/error response
- **SearXNG results have different schema** — `results[].url` vs `results[].link`; normalize before processing
- Both tools have independent rate limits; if doing 10+ searches, space them out
