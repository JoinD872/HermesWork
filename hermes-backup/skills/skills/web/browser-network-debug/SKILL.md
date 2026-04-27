---
name: browser-network-debug
description: 排查"curl 能访问但浏览器(agent-browser/Chromium)无法访问"的问题
triggers:
  - 浏览器超时
  - curl 能通但 browser_navigate 超时
  - ERR_TUNNEL_CONNECTION_FAILED
  - net::ERR_*
---

# 浏览器网络排查流程

## 排查步骤

### Step 1: 确认 curl 是否真的能通
```bash
curl -s --max-time 10 -o /dev/null -w "%{http_code}" https://目标网站
```
- curl 通 → 问题在浏览器层
- curl 也不通 → 网络层问题，先解决网络

### Step 2: 检查 IPv4 vs IPv6
```bash
curl -4 --max-time 5 -o /dev/null -w "%{http_code}" https://目标网站  # IPv4
curl -6 --max-time 5 -o /dev/null -w "%{http_code}" https://目标网站  # IPv6
```
- 仅 IPv4 通 → 可能是 IPv6 路由问题，浏览器可能优先走 IPv6

### Step 3: 检查代理配置
检查 Xray/Clash 是否是标准 HTTP 代理（SOCKS 也算）：
```bash
# 测试是否是 HTTP 代理
curl -x http://127.0.0.1:8080 https://www.baidu.com --connect-timeout 5
# 如果返回 400/407 而不是 404 → 是 HTTP 代理
# 如果返回 404 → 可能是 VLESS/VMess/SSH 等非 HTTP 协议
```
**重要：** VLESS WebSocket 协议不是 HTTP 代理，浏览器配置 `http://proxy` 无法使用。

### Step 4: 检查浏览器 daemon 状态
```bash
# 重启浏览器 daemon
agent-browser close
sleep 2
agent-browser open https://example.com
```

### Step 5: 长超时测试
```bash
agent-browser open https://目标网站 --timeout 60000
```

### Step 6: 截图看实际状态
```bash
browser_navigate → 超时
browser_snapshot  # 看是空页面还是部分加载
browser_vision    # 截图看实际渲染情况
```

## 常见原因

| 原因 | 症状 | 解决方案 |
|------|------|----------|
| 路由过滤（GFW/ISP） | curl 通浏览器不通 | 使用代理/CF Workers |
| IPv6 路由有问题 | curl -4 通但 -6 失败 | 浏览器强制 IPv4 或禁用 IPv6 |
| Xray VLESS WS | 配置是 VLESS WS 但配成了 HTTP 代理 | 浏览器不支持 VLESS WS，需要其他方案 |
| TLS SNI 过滤 | TCP 握手成功但 TLS 失败 | 换 IP 或用代理 |
| **Cloudflare 反爬拦截** | curl 返回 200 但浏览器 403/挑战页面 | **改用 curl 抓页面内容**，绕过浏览器 |
| **Cloudflare + 域名差异** | 同站点不同域名响应不同 | 先用 curl 测试各域名，实测为准 |

## 已知 Cloudflare 拦截案例（curl 可通）

| 网站 | curl 状态 | 浏览器状态 | 备注 |
|------|-----------|-----------|------|
| dev.epicgames.com | ✅ 200 | ❌ 403 | Cloudflare 拦截浏览器 |
| docs.unrealengine.com | ❌ 403 | ❌ 403 | 整个域名被拦截 |

> **核心原则**：遇到 Cloudflare 拦截，先用 curl 测试目标 URL。如果 curl 返回 200，立即改用 `curl -sL URL` + `terminal` 抓取内容，完全绕过浏览器。

**示例场景**：抓取 Epic UE5.7 文档
```bash
# 错误：浏览器被拦截
browser_navigate → 403 Cloudflare

# 正确：curl 直接拿内容
curl -sL "https://dev.epicgames.com/documentation/..." | grep -oP '...'
```

**跨 Agent 协作原则**：如果 subagent 遇到 Cloudflare 拦截导致浏览器失败，直接告知它用 curl 代替，不需要复杂的代理配置。

## 降级方案

当浏览器无法访问时，降级到 curl + web_extract：
```bash
curl -s https://目标页面 > /tmp/page.html
# 然后用 web_extract 工具处理
```
