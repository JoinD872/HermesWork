---
name: gif-search
description: GIF 搜索下载 — 使用 curl 从 Tenor 搜索和下载 GIF，无依赖，只需 curl 和 jq
version: 1.0.0
tags: [media, gif, tenor, search, download]
---

# GIF Search Skill

从 Tenor 搜索和下载 GIF，使用纯 curl，无需 API key。

## 使用

```bash
# 搜索 GIF
curl "https://tenor.googleapis.com/v2/search?q=hello&key=YOUR_KEY&limit=10"

# 下载 GIF
curl -o output.gif "GIF_URL"
```

## 用途

- 表情包/GIF 搜索
- 飞书/聊天工具发送 GIF
- 创意内容制作
