---
name: linear
description: Linear API — 通过 GraphQL 管理 issues/projects/teams，创建/更新/搜索/组织 issue，无需 OAuth 只需 API key
version: 1.0.0
tags: [productivity, linear, project-management, issues, api]
---

# Linear Skill

通过 Linear GraphQL API 管理 issues、projects 和 teams。

## 核心功能

- **Issues**：创建/更新/搜索/标签/指派/关联 PR
- **Projects**：项目管理
- **Teams**：团队管理
- **工作流**：自动化 issue 状态流转

## 认证

只需 Linear API Key，无需 OAuth：

```bash
export LINEAR_API_KEY=your_api_key
```

## 使用

```bash
# 搜索 issues
curl -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_API_KEY" \
  -d '{"query": "{ issues(first: 10) { nodes { id title state } } }"}'

# 创建 issue
curl -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_API_KEY" \
  -d '{"query": "mutation { issueCreate(input: {title: \"Bug\"}) { success } }"}'
```

所有操作通过 curl，无需额外依赖。
