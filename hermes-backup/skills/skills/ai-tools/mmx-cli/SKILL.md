---
name: mmx-cli
description: MMX CLI 全功能指南 — MiniMax 命令行工具，支持图片理解/生成、视频、音乐、语音合成、文本对话、网页搜索、配额查询
tags: [minimax, cli, image, video, music, speech, search]
category: ai-tools
---

# MMX CLI 全功能指南

## 基础信息

**安装：** `npm install -g mmx-cli`
**版本：** `mmx --version`
**认证：** `mmx auth login --api-key <KEY>`（存独立 credential store，不依赖环境变量）
**状态：** `mmx auth status`

---

## 全部功能模块

| 模块 | 功能 | 命令 |
|------|------|------|
| **vision** | 图片理解 | `mmx vision describe <图片路径>` |
| **image** | 图片生成 | `mmx image generate --prompt "描述"` |
| **video** | 视频生成 | `mmx video generate --prompt "描述"` |
| **music** | 音乐生成 | `mmx music generate --prompt "描述"` |
| **speech** | 语音合成 | `mmx speech synthesize --text "文本" --voice "音色名"` |
| **text** | 文本对话 | `mmx text chat --prompt "问题"` |
| **search** | 网页搜索 | `mmx search query <关键词>` |
| **auth** | 认证管理 | `mmx auth status/login/logout` |
| **quota** | 配额查询 | `mmx quota show` |
| **config** | 配置管理 | `mmx config show/set` |
| **update** | 版本更新 | `mmx update` |

---

## 常用命令详解

### 截图/图片理解（最常用）
```bash
mmx vision describe /path/to/image.jpg
```

### 网页搜索
```bash
mmx search query <关键词>
```

### 文本对话
```bash
mmx text chat --prompt "你的问题"
```

### 语音合成
```bash
# 查看可用音色
mmx speech voices

# 合成语音
mmx speech synthesize --text "你好" --voice "中文音色名"
```

### 图片生成
```bash
mmx image generate --prompt "一幅画：日出海洋"
```

### 配额查询
```bash
mmx quota show
```

---

## 全局参数

| 参数 | 说明 |
|------|------|
| `--api-key <key>` | 临时指定 API key（覆盖配置） |
| `--region <region>` | 区域：global（默认）或 cn |
| `--output <format>` | 输出格式：text（默认）或 json |
| `--quiet` | 静默模式，只输出结果 |
| `--verbose` | 显示完整 HTTP 请求/响应 |
| `--timeout <seconds>` | 请求超时，默认 300 秒 |
| `--non-interactive` | CI/agent 模式（禁用交互提示） |

---

## 已知限制

- MiniMax 国内版 region 设为 `cn`，base_url 是 `https://api.minimax.cn/v1`
- `mmx auth status` 显示 `No API key found` 说明 key 未配置好
- Token Plan Key 走 MCP 有平台级 1004 bug，**统一走 MMX CLI**
- **图片生成从 VPS 不可用**（见下方"图片生成故障排查"）

---

## 图片生成故障排查

**症状**：`mmx image generate` 报错 `code: 6, Network request failed (HTTP 200)`

**根因**：从这台 VPS（洛杉矶 HostPapa IP）访问 `image.minimaxi.com` DNS 不可达。文本 API（`api.minimaxi.com`）正常，图片生成独立域名被墙。

**诊断命令**：
```bash
curl -sv --connect-timeout 5 https://api.minimaxi.com/  # 应通
curl -sv --connect-timeout 5 https://image.minimaxi.com/  # 应不通
```

**备用方案（VPS 可用）**：
```bash
curl -fsSL --connect-timeout 60 \
  "https://image.pollinations.ai/prompt/<URL编码prompt>?width=512&height=512&model=flux" \
  -o /path/to/output.png
```

**注意**：切换 region 到 `global` 会报 `invalid api key`，CN key 不适用于 global 端点。

---

## 错误排查

- **1004 login fail**：不要走 MCP，直接用 MMX CLI
- **No API key found**：执行 `mmx auth login --api-key <KEY>`
- **timeout**：加 `--timeout 600` 延长超时
- **图片生成 code 6**：见上方图片生成故障排查
