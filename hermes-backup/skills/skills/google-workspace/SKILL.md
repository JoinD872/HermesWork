---
name: google-workspace
description: Google 工作区集成 — Gmail/日历/Drive/联系人/Sheets/Docs，使用 Hermes 管理的 OAuth2，优先 gws CLI
version: 1.0.0
tags: [productivity, google, gmail, calendar, drive, docs, workspace]
---

# Google Workspace Skill

通过 Gmail、Google Calendar、Google Drive、Google Contacts、Google Sheets、Google Docs 管理日常工作。

## 核心功能

- **Gmail**：读取/发送/搜索/标签管理
- **Calendar**：创建/查询/更新日程
- **Drive**：上传/下载/分享文件
- **Contacts**：联系人管理
- **Sheets**：读取/写入/更新电子表格
- **Docs**：读取/创建/更新文档

## 认证方式

- 优先使用 `gws` CLI（更广泛的 API 覆盖）
- 回退使用 Python Google Client Library
- OAuth2 由 Hermes 管理

## 使用场景

- 邮件处理
- 日历管理
- 文档协作
- 数据表格操作
