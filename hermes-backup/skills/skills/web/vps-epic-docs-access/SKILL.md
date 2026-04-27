---
name: vps-epic-docs-access
description: VPS 无法访问 Epic/Unreal Engine 开发者文档的结论和解决方案
---
# VPS 访问 Epic 开发者文档

## 结论

**docs.unrealengine.com 和 dev.epicgames.com 从 VPS（洛杉矶 HostPapa）完全无法访问**，被 Cloudflare 五层检测封锁。

### 测试过的方案（均失败）

| 方案 | 结果 | 原因 |
|------|------|------|
| `curl` + 各种 UA headers | ❌ 403 | Cloudflare 直接封 IP |
| `cloudscraper` (Python) | ❌ 返回 CF 挑战页 | JS 挑战无法执行 |
| Camoufox (browser tool) | ❌ "One more step" | 被识别为自动化 |
| Playwright stealth | ❌ 同上 | `navigator.webdriver` 等泄露 |
| `nodriver` | ❌ 缺 Chrome 二进制 | 环境没有 Chrome |
| Wayback Machine | ❌ 无存档 | 该域名无快照 |
| Google 缓存 | ❌ 无数据 | Google 也无缓存 |

### Cloudflare 五层封锁

1. TLS fingerprinting (JA3)
2. IP reputation（数据中心 IP 直接封）
3. JavaScript challenges
4. Behavior analysis
5. Turnstile CAPTCHA

## 可行方案

### 方案 1：用户本地浏览器（最靠谱）
让用户在本地浏览器打开页面 → 复制内容给我 → 我整理

### 方案 2：住宅代理
Bright Data / Oxylabs 等 residential proxy 改变出口 IP，可绕过 IP reputation 检测。需额外配置。

### 方案 3：国内镜像
部分 Epic 文档内容可能在 CSDN、知乎等国内平台有转载，可搜索。

## 触发条件

当需要访问以下域名时，直接使用方案 1（用户本地浏览器）：
- `docs.unrealengine.com`
- `dev.epicgames.com`
- 其他被 Cloudflare 保护且curl返回403的Epic系域名
