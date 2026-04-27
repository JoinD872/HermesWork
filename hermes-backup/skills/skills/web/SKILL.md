---
name: search-tools
description: VPS 搜索工具 — SearXNG / mcp_minimax_plan_web_search / 浏览器搜索 各工具用法和质量对比
version: 1.0.0
tags: [search, searxng, vps, network]
---

# VPS 搜索工具

## 可用工具对比

| 工具 | 地址 | 质量 | VPS 可用 | 备注 |
|------|------|------|---------|------|
| SearXNG | localhost:8888 | ✅ 高（Google/DDG） | ✅ | 已部署，反爬最强 |
| mcp_minimax_plan_web_search | MCP | ❌ 差 | ✅ | 底层搜索引擎不行 |
| Playwright 浏览器 Google | — | ✅ 高 | ⚠️ 需代理 | 被反爬时可能失败 |

---

## SearXNG 用法

VPS 上已运行 SearXNG（docker: searxng，端口 8888）。

### 基础搜索（curl）

```bash
curl -s "http://localhost:8888/search?q=关键词&format=json&engines=google" | python3 -c "
import sys,json
d=json.load(sys.stdin)
for r in d['results'][:5]:
    print(r['title'])
"
```

### 指定引擎

```
&engines=google
&engines=duckduckgo
&engines=startpage
&engines=google,duckduckgo  # 多引擎
```

### 注意事项

- SearXNG 容器内能访问 Google/DuckDuckGo，VPS 本身直连不了海外
- 搜中文内容建议用 `google` 引擎
- Brave 引擎默认被限流（too many requests），可用 `google` 或 `startpage` 代替

---

## 常见问题

**SearXNG 搜不到结果？**
→ 检查 `unresponsive_engines` 字段，可能是引擎被墙了，换用其他引擎。

**VPS 网络完全不通外网？**
→ SearXNG 是 VPS 上唯一能间接访问 Google 的渠道。

---

## 历史背景

- `mcp_minimax_plan_web_search` 底层搜索引擎质量差（搜 "minimax web search API" 出来消防公司）
- 排查发现是 SearXNG 在跑，说明 VPS 访问 Google 是通的
- 因此 SearXNG 是目前最可靠的搜索方案
