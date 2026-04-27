---
name: web-page-detail-extract
description: 网页完整信息提取 — 用户给 URL 后直接进页面抓全部内容，不依赖搜索
triggers:
  - 用户发来 URL 要求查看/整理内容
  - 要求获取网页完整配置/规格/价格信息
---

# Web Page Detail Extract · 网页完整信息提取

## 核心原则
**URL 优先，不依赖搜索。** 用户给了链接就直接进页面抓，不要先搜索再找内容。

## 标准工作流

### 1. 直接导航
```
browser_navigate(url)
```
直接去 URL，不经过搜索引擎。

### 2. 展开所有折叠内容
用 `browser_console` 执行 JS，遍历点击所有可折叠元素：
```javascript
document.querySelectorAll('[class*="toggle"], [class*="collapse"], [class*="accordion"], .sectionheader, .card-header, [data-toggle], summary, details:not([open])').forEach(el => { try { el.click(); } catch(e) {} });
```
等 500ms 后再提取。

### 3. 提取完整文本（关键！）
**必须用 `browser_console` 的 `innerText`，不要依赖 `browser_snapshot`**。
`browser_snapshot` 超过 ~8000 char 会截断或 LLM 摘要，内容不完整。

正确方式：
```javascript
// 通用全文提取（直接 innerText，不过滤选择器）
document.body.innerText

// 产品页精确提取
document.querySelector('table')?.innerText ||
document.querySelectorAll('[class*="product"] p, [class*="product"] li, [class*="product"] h3, [class*="product"] h4').map(el => el.innerText).join('\n')
```

`browser_console` 返回完整文本，不会截断。

### 4. 页面截图辅助判断
当 JS 展开后 `innerText` 仍不完整（可能是 JS 动态渲染），用 `browser_vision` 截图 + AI 分析。

### 5. JSON API 降级
如果 `?format=json` 返回 HTML，说明该站不支持 JSON，直接解析 HTML。

## Hermes 辅助模型（重要！）

Hermes 内置了 `web_extract` auxiliary model，专用于页面摘要提取：

```yaml
auxiliary:
  web_extract:
    provider: "auto"    # 默认 Gemini Flash
    timeout: 360         # 6分钟
```

这解释了为什么 OpenClaw 抓取更完整 — 如果配置了更强的 extraction model，页面内容会被更完整地分析和返回。

如果抓取内容不完整，检查是否可以通过配置 `auxiliary.web_extract.model` 换一个支持更长上下文的模型。

## Reddit / LowEndTalk / Trustpilot 拦截 → 备用方案（2026-04-24 新增）

研究 RackNerd 和 Hermes 等项目时，Reddit 和 LowEndTalk 经常被目标站拦截，需备用路径：

| 目标站 | 拦截原因 | 备用方案 |
|--------|---------|---------|
| `reddit.com`（r/VPS, r/openclaw 等） | VPS 出口 IP 被 Reddit 风控屏蔽 | `browser_navigate` 直接进页面（browser tool 仍可访问） |
| `lowendtalk.com` | Cloudflare 保护 + 页面 JS challenge | 改用 `lowendbox.com`（同社区主办，内容可正常抓取） |
| Trustpilot 个别页 | 偶尔 JS challenge | `browser_navigate` 重试一次即可 |

**研究流程**：Reddit帖子 → `browser_navigate(url)` 直接抓 → 页面显示 blocked → 等几秒再试或用 `browser_vision` 辅助

> 注意：SearXNG 搜索结果里 Reddit 链接无法从 terminal curl 访问，但 browser tool 可以绕过。

## Epic/UE 文档站 Cloudflare 拦截 → 第三方游戏媒体（2026-04-22 新增）
**症状**：`dev.epicgames.com` → 403；`docs.unrealengine.com` → Cloudflare challenge 页面
**原因**：Epic 文档站用 Cloudflare 保护，同时拦截 browser 和 curl 请求（连 curl 都返回 challenge HTML）
**解决**：绕道第三方游戏新闻站，这些站大量转载 UE 文档且**可访问**：
- `80.lv` — ✅ 可正常抓取，内容最详细
- `cgchannel.com` — ✅ 可正常抓取
- `forums.unrealengine.com` — ✅ 发布帖可访问
**搜索技巧**：`site:80.lv OR site:cgchannel.com "unreal engine 5.7"` 找对应文章
**结论**：遇到 Epic 官方站拦截 → 改搜 80.lv / CGChannel，内容往往比官方更详细易读

## 外国技术社区快速跳转（2026-04-24 新增）

研究 Hermes Agent / RackNerd 时，直接去这些 URL 获取第一手讨论：

### Hermes Agent
| 平台 | URL | 价值 |
|------|-----|------|
| GitHub Issues（最热） | `github.com/nousresearch/hermes-agent/issues?q=is%3Aissue+sort%3Acomments-desc` | 按评论数排序，最高技术含量 |
| HuggingFace Discuss | `discuss.huggingface.co/t/hermes-agent-persistent-memory...` | 高质量架构分析帖 |
| DEV Community | `dev.to/arshtechpro/hermes-agent-a-self-improving-ai-agent...` | 开发者实测 |
| Reddit r/openclaw | `reddit.com/r/openclaw/` | Hermes vs OpenClaw 主战场，103k 成员 |
| r/hermesagent | `reddit.com/r/hermesagent/` | 非官方 Hermes 社区 |

### RackNerd VPS
| 平台 | URL | 价值 |
|------|-----|------|
| Reddit r/VPS | `reddit.com/r/VPS/` | 最真实用户反馈，多年持续 |
| Trustpilot | `trustpilot.com/review/racknerd.com` | 4.3/5（375条），第三方独立评分 |
| BestUSAVPS | `bestusavps.com/reviews/racknerd/` | 14个月实测，99.93% uptime 数据 |
| LowEndBox | `lowendbox.com/` | VPS 优惠聚合 + 社区博客，可访问 |
| GitHub 用户评测 | `github.com/yel199/racknerd-vps-reviews` | 用户自发综合评测 |

> 所有 Reddit 链接在 VPS 上被屏蔽，用 `browser_navigate` 直接进即可绕过。

## 官网 404 → Web Archive → 中文汇总站（爬取顺序）
1. 直接进官网/客户入口（最完整）
2. 官网 404 → Web Archive（`https://web.archive.org/web/2025/https://目标URL`）
3. 中文汇总站（`www.laozuo.org`、`idccoupon.com`）— **信息常不完整**，仅作参考，缺少字段：RAID类型、系统限制、付款方式、具体机房

### WSL2 网络受限
当前环境只能访问白名单域名，大多数搜索/AI/GitHub 相关网站被墙。

| 能访问 | 状态 |
|--------|------|
| `hermes-agent.nousresearch.com/docs` | ✅ 官方文档（官方文档站） |
| `hermes.xaapi.ai` | ✅ 中文文档（仅首页） |
| `my.racknerd.com` | ✅ 客户入口 |
| `cn.bing.com` | ✅ |
| `www.laozuo.org` | ✅ 中文汇总站 |
| `searxng.org` | ❌ GitHub Pages 死站 |
| `searx.party` | ⚠️ 限速 429 |
| `github.com` | ❌ 超时 |
| `duckduckgo.com` | ❌ 超时 |
| `metager.org` | ❌ 超时 |
| `agentskills.io` | ❌ 重定向过多 |

**结论：有 URL → 直接进；没 URL → 搜索但质量受限。**

## 验证步骤
1. 所有折叠项已展开
2. 所有产品信息完整提取（名称/CPU/内存/SSD/流量/价格/机房/附加信息）
3. 无内容被截断

## Hermes 官方文档 URL 结构规律（WSL2 下可用）

官方文档站 `hermes-agent.nousresearch.com/docs` 可访问，但路径结构有规律：
- 文档首页 → `https://hermes-agent.nousresearch.com/docs`
- Memory → `/docs/user-guide/features/memory`
- Skills → `/docs/user-guide/features/skills`
- Configuration → `/docs/user-guide/configuration`
- Tips → `/docs/guides/tips`
- Migrate from OpenClaw → `/docs/guides/migrate-from-openclaw`

**规律**：`/docs/{category}/{page}` 或 `/docs/user-guide/features/{feature}`

中文镜像站 `hermes.xaapi.ai` 仅首页可用，子页面路径不一致，优先用官方文档。

## 示例
- RackNerd BF2025: `https://my.racknerd.com/index.php?rp=/store/blackfriday2025`
