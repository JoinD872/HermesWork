---
name: obsidian
description: Obsidian 笔记库读写搜索 — Dataview 查询/ Vault 管理/双向链接，支持 Obsidian Sync 无头模式
version: 1.0.0
tags: [note-taking, obsidian, knowledge-base, vault, dataview]
---

# Obsidian Skill

读写和管理 Obsidian 笔记库，支持双向链接、Dataview 查询、Vault 管理。

## 核心功能

- **读写笔记**：读取/创建/更新 .md 文件
- **Dataview 查询**：使用类 SQL 语法查询笔记库
- **双向链接**：`[[wikilinks]]` 支持
- **Vault 管理**：操作文件夹和文件结构
- **Obsidian Sync 无头模式**：服务器上同步，桌面端浏览

## Obsidian Headless（服务器）

在无头机器上使用 obsidian-headless 同步 vault：

```bash
npm install -g obsidian-headless
ob login --email <email> --password '<password>'
ob sync-create-remote --name "My Wiki"
cd ~/vault && ob sync-setup --vault "<vault-id>"
ob sync --continuous
```

## 依赖

- Obsidian 应用（桌面端浏览）
- obsidian-headless（无头同步）
- Dataview 插件（查询功能）
