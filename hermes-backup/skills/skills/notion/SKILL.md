---
name: notion
description: Notion API — 通过 curl 管理 pages/databases/blocks，搜索/创建/更新/查询 Notion 工作区
version: 1.0.0
tags: [productivity, notion, api, pages, databases, notes]
---

# Notion Skill

通过 Notion API 直接从终端管理 Notion pages、databases 和 blocks。

## 核心功能

- **Pages**：读取/创建/更新/归档页面
- **Databases**：创建/查询/过滤/排序数据库
- **Blocks**：追加/更新/删除块
- **搜索**：全工作区搜索页面

## 认证

需要 Notion Integration Token，设置为 `NOTION_API_KEY` 环境变量。

## 使用

```bash
# 创建页面
curl -X POST https://api.notion.com/v1/pages \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -d '{"parent": {"database_id": "DB_ID"}, "properties": {...}}'

# 查询数据库
curl -X POST https://api.notion.com/v1/databases/DB_ID/query \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -d '{"filter": {...}}'
```
