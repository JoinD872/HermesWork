---
name: research-fallback-strategy
description: When standard search tools fail (MCP, SearXNG, browser), fall back to arXiv for AI/ML research and direct source navigation
triggers:
  - search returns empty
  - all search tools blocked
  - cron research task
---

# Research Fallback Strategy — When Search Tools Fail

## Context
When conducting research in cron/automated contexts, standard search tools (MCP, SearXNG, Bing, Google) often fail due to:
- API errors (404s, endpoint changes)
- Cloudflare bot detection blocks
- Network restrictions in VPS environments

## Fallback Sequence (in order)

1. **arXiv** (`arxiv.org`) — Most reliable for AI/ML research
   - Direct navigation to `https://arxiv.org/search/?searchtype=all&query=...`
   - Returns actual academic papers with abstracts
   - Example: Multi-agent delegation, LLM optimization topics work well
   - **Note**: Not yet verified failing from this VPS; try before internal knowledge

2. **PubMed** (`pubmed.ncbi.nlm.nih.gov`) — For health/medical topics
   - Use shorter, more specific queries (broad queries return 0 results)
   - Structure: `https://pubmed.ncbi.nlm.nih.gov/?term=keyword1+keyword2`

3. **Direct Source Navigation** — For known domains
   - If you know the paper title/author, go directly to the abstract page
   - arXiv IDs can be navigated directly: `https://arxiv.org/abs/YYMM.NNNNN`

4. **Session Search** — Check past conversations
   - `session_search()` often has relevant context already researched
   - Use keywords from your research task to recall prior work

5. **Internal Knowledge Base** — Last resort when all tools fail
   - Compile from known skills, memory files, and general domain knowledge
   - Clearly note "基于内部知识库整理，建议有条件时二次验证" in output
   - Better than producing no research at all

## Key Lesson
When all search tools fail, **start with arXiv** for AI/ML topics before trying more complex browser automation. arXiv's search is academic-grade and rarely blocks automated access.

## Verified Failure Modes (VPS 192.3.241.244 — 2026-04-26)

| Tool | Status | Error |
|------|--------|-------|
| SearXNG MCP | ❌ Empty results | Returns `{"results":[]}` with no error |
| MiniMax web_search | ❌ 404 | `404 Page not found for url: .../v1/v1/coding_plan/search` |
| Google | ❌ IP blocked | "IP address: 192.3.241.244" shown in CAPTCHA page |
| DuckDuckGo | ❌ CAPTCHA | "bots use DuckDuckGo too" challenge |
| Browser-based search | ❌ Blocked | All major engines trigger bot detection |

**Conclusion**: From this VPS, only arXiv/PuMed direct navigation and session_search remain viable. Internal knowledge base is the final fallback.

## Cron Research Output Destinations

When running as a scheduled research cron job, push summaries to:

| Content | Destination |
|---------|-------------|
| Multi-agent collaboration, agent memory, automation | `feishu:oc_ec9adb3139cd38ac706cd7a54c4d059d` (研究员群) |
| VPS/proxy/dev mirrors | `feishu:oc_8391fa2b38acbd759ff75ab3616d5d1f` (DM 小H) |
| Sleep health, nutrition | `feishu:oc_6dbf15aa718c29adca8d085017930a71` (健康群) |

Format: 2-3 sentences per sub-topic, title with 📌 小研研究 | [方向]
