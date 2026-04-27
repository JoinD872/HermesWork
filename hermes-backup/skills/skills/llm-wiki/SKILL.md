---
name: llm-wiki
description: Karpathy LLM Wiki 知识库模式 — Layer1原始源/Layer2 Wiki页面/Layer3 Schema，摄入/查询/检查/一致性维护，支持 Obsidian 集成
version: 2.0.0
tags: [research, wiki, knowledge-base, markdown, notes, rag-alternative]
---

# Karpathy's LLM Wiki Skill

基于 Andrej Karpathy 的 LLM Wiki 模式构建持久化知识库。

## 三层架构

```
wiki/
├── SCHEMA.md          # 规范/结构/领域配置
├── index.md           # 内容目录（一行摘要）
├── log.md             # 时间顺序操作日志
├── raw/               # Layer 1: 不可变原始材料
│   ├── articles/      # 网页文章
│   ├── papers/         # PDF / arxiv 论文
│   ├── transcripts/    # 会议记录/访谈
│   └── assets/        # 图片/图表
├── entities/          # Layer 2: 实体页面
├── concepts/          # Layer 2: 概念页面
├── comparisons/        # Layer 2: 对比分析
└── queries/           # Layer 2: 归档查询结果
```

## 核心操作

1. **Ingest**：摄入 URL/文件/文本 → 保存 raw → 讨论 → 写/更新 wiki 页面
2. **Query**：读 index.md → 搜索相关页 → 综合回答 → 可选归档答案
3. **Lint**：孤儿页面/断链/索引完整性/frontmatter/过时内容检查

## Schema 规范

- 文件名：小写 + 连字符
- 每次更新 bump `updated` 日期
- 新页面必须加入 index.md
- 每项操作追加到 log.md
- Wiki 页面最小 2 个 outbound `[[wikilinks]]`

## Obsidian 集成

wiki 目录直接作为 Obsidian vault 使用：
- `[[wikilinks]]` 可点击
- Graph View 可视化知识网络
- Dataview 插件查询
