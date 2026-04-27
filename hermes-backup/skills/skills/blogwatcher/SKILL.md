---
name: blogwatcher
description: RSS/Atom 博客订阅监控 — blogwatcher-cli 工具，自动发现订阅/OPML导入/已读未读跟踪
version: 2.0.0
tags: [research, RSS, blogs, feed-reader, monitoring]
---

# Blogwatcher Skill

通过 blogwatcher-cli 跟踪博客和 RSS/Atom 订阅更新。

## 安装

```bash
# Go
go install github.com/JulienTant/blogwatcher-cli/cmd/blogwatcher-cli@latest

# Docker
docker run --rm -v blogwatcher-cli:/data ghcr.io/julientant/blogwatcher-cli scan

# Linux binary
curl -sL https://github.com/JulienTant/blogwatcher-cli/releases/latest/download/blogwatcher-cli_linux_amd64.tar.gz | tar xz -C /usr/local/bin blogwatcher-cli
```

## 常用命令

```bash
# 添加博客
blogwatcher-cli add "My Blog" https://example.com

# 扫描所有
blogwatcher-cli scan

# 列出未读
blogwatcher-cli articles

# 标记已读
blogwatcher-cli read 1

# 导入 OPML
blogwatcher-cli import subscriptions.opml
```

## 环境变量

- `BLOGWATCHER_DB` — SQLite 数据库路径
- `BLOGWATCHER_WORKERS` — 并发扫描工作数（默认8）
- `BLOGWATCHER_SILENT` — 静默模式
