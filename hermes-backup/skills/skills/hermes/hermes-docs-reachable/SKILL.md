---
name: hermes-docs-reachable
description: Hermes 官方文档站在 WSL2 网络下的可达性，以及中文镜像的 URL 结构坑
category: hermes
---
# Hermes 官方文档站可用性

## 网络可达性（WSL2 环境）

| 站点 | 状态 | 说明 |
|------|------|------|
| `hermes-agent.nousresearch.com/docs` | ✅ 200 | 官方文档，主站 |
| `hermes.xaapi.ai` | ✅ 200（仅首页） | 中文镜像，子页面全部 404 |
| `hermesagent.org.cn` | ✅ 200 | 另一个中文镜像 |

## 关键坑：中文镜像 URL 结构与官方不同

`hermes.xaapi.ai` 的子页面路径**不是**官方路径，直接拼 `/docs/xxx` 会 404。

错误示例：
- ❌ `hermes.xaapi.ai/docs` → 404
- ❌ `hermes.xaapi.ai/docs/reference/faq` → 404
- ❌ `hermes.xaapi.ai/docs/advanced/openclaw-migration` → 404

正确做法：去官方站 `hermes-agent.nousresearch.com/docs` 查子页面路径。

## 官方文档值得看的页面

- Installation: `https://hermes-agent.nousresearch.com/docs/getting-started/installation`
- Configuration: `https://hermes-agent.nousresearch.com/docs/getting-started/configuration`
- Memory System: `https://hermes-agent.nousresearch.com/docs/using-hermes/memory`
- Skills System: `https://hermes-agent.nousresearch.com/docs/using-hermes/skills`
- Tips & Best Practices: `https://hermes-agent.nousresearch.com/docs/guides/tips`
- MCP Integration: `https://hermes-agent.nousresearch.com/docs/integrations/mcp`
