---
name: hermes-browser-toolset
description: Hermes Agent browser toolset configuration — why browser automation may silently fail and how to diagnose it
category: devops
tags: [browser, camoufox, playwright, config, troubleshooting]
version: 2026-04-09
---

# Hermes Browser Toolset 配置指南

## 症状
browser_navigate / browser_snapshot / browser_click 等 browser 工具调用后返回内容很少、或工具似乎不可用，但没有任何报错。

## 根本原因
`config.yaml` 的 `toolsets` 数组必须显式包含 `browser`。默认安装时可能只有 `hermes-cli`，导致 browser toolset 不可用。

```yaml
# ✅ 正确 — 必须有 browser
toolsets:
  - hermes-cli
  - browser

# ❌ 错误 — 缺少 browser（browser 工具全部静默失效）
toolsets:
  - hermes-cli
```

## 验证方法

在 `config.yaml` 中找到 `toolsets` 部分，确认包含 `browser`。

正常情况：browser_navigate 访问 my.racknerd.com 应返回 5,000+ 字符的完整页面内容。
异常情况：返回很少内容（几百字符或更少）。

## 浏览器引擎优先级

Hermes Agent 的 browser toolset 按以下顺序选择引擎：

1. **Camoufox**（首选）— 反检测 Firefox 浏览器，爬取动态内容最佳
2. **Playwright**（降级备选）— 当 Camoufox 不可用时自动降级，API 完全兼容

## Camoufox 与 Playwright 对比

| 特性 | Camoufox | Playwright |
|------|----------|------------|
| 内核 | Firefox（反检测） | Chromium/Firefox/WebKit |
| 动态内容 | ✅ 强 | ✅ 强 |
| 反爬对抗 | ✅ 专为爬虫设计 | 一般 |
| 内核下载 | 需要 GitHub（国内可能超时） | 预装 |
| 安装难度 | 较高 | 简单 |
| 自动降级 | — | 是 |

## 常见问题

### Q: browser 工具有时候返回内容很少
**A**: 检查 toolsets 是否包含 `browser`，然后检查 config 中 `browser` section 的 `web_extract` auxiliary 是否配置了模型。

### Q: Camoufox 内核下载失败
**A**: WSL2 环境下 GitHub 被墙，导致浏览器内核下载超时。解决方案：
1. 挂梯子手动下载内核
2. 使用 Playwright 作为替代（自动降级，API 相同）
3. Cron job 定时提醒：设置 21:00 推飞书提醒手动处理

### Q: Playwright 和 Camoufox 能否共存
**A**: 可以。安装 Camoufox 不会破坏 Playwright。Hermes 自动检测可用引擎。

## 配置检查清单

```yaml
# config.yaml 应包含以下内容：

toolsets:
  - hermes-cli
  - browser        # ← 必须有

browser:           # ← 可选，增强配置
  auxiliary:
    model: gemini-2.0-flash
    provider: google
```

## 故障排除流程

```
browser 工具异常
    │
    ├─→ 检查 config.yaml toolsets
    │       │
    │       ├─→ 没有 browser → 添加后重启 gateway
    │       └─→ 有 browser → 继续
    │
    ├─→ 检查 Camoufox 可用性
    │       │
    │       ├─→ import 失败 → 安装内核或确认 Playwright 可用
    │       └─→ import 成功 → 继续
    │
    └─→ 检查 web_extract auxiliary
            │
            └─→ 没有配置 → 添加 gemini-2.0-flash auxiliary
```

## 相关 Skill

- `devops/camoufox-install` — Camoufox 安装完整指南，包含 Playwright 降级备选
- `web/web-page-detail-extract` — 完整页面信息提取工作流
