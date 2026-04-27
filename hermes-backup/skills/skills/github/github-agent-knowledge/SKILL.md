---
name: github-agent-knowledge
description: GitHub Copilot Agent 体系知识 — 基于官方文档。包含 Custom Agents、Agent Skills 开放标准、Agentic Memory 机制。对标我的 Skills 体系，理解差距与改进方向。
version: 1.0.0
metadata:
  hermes:
    tags: [github, copilot, agents, skills, memory]
---

# GitHub Agent Knowledge

## Agent Skills 开放标准（重要！）

GitHub Copilot 的 Agent Skills 是一个 **16.7k stars 的开放标准**，被多个 AI 系统采用：https://github.com/agentskills/agentskills

### 目录结构（与我的 Skills 高度一致）

```
skill-name/
├── SKILL.md           # 必需：YAML frontmatter + 使用说明
├── scripts/           # 可选：可执行脚本
├── references/       # 可选：文档/参考资料
├── assets/          # 可选：模板、图片等资源
└── ...               # 任意额外文件
```

### SKILL.md 格式

```yaml
---
name: skill-name
description: 技能描述
version: 1.0.0  # 可选
readiness: stable|experimental|deprecated  # 可选，生命周期状态
allowed_tools:  # 可选，限制可用工具
  - browser_navigate
  - terminal
---
# Markdown 使用说明
```

### 我的 Skills 体系对比

| 特性 | 我的 Skills | Agent Skills Spec |
|------|------------|------------------|
| 目录结构 | ✅ `SKILL.md` + 子目录 | ✅ 相同 |
| 格式 | ✅ YAML frontmatter + MD | ✅ 相同 |
| 触发字段 | ✅ `name` `description` | ✅ 相同 |
| 环境检查 | ✅ `missing_required_*` | ❌ 无 |
| 生命周期 | ❌ 无 | ✅ `readiness` 字段 |
| 工具限制 | ❌ 无 | ✅ `allowed_tools` |
| 强制策略 | ❌ 无 | ✅ `force_resolution` |

**我的不足**：
1. 没有 `readiness` — 无法标记 skill 稳定性
2. 没有 `allowed_tools` — 无法限制 skill 只能使用特定工具
3. 没有 `force_resolution` — 冲突处理策略不明确

## Custom Agents

GitHub Copilot Custom Agents = 我理解的"专业角色"。通过 Markdown agent profile 定义，放在：
- 仓库级：`.github/agents/NAME.md`
- 组织/企业级：`.github-private/agents/NAME.md`

### Agent Profile 示例

```yaml
---
name: readme-creator
description: Agent specializing in creating and improving README files
---
You are a documentation specialist focused on README files.
Your scope is limited to README files or other related documentation files only.
```

这跟我的 Skill 体系本质上是一样的思路，只是应用层不同（Copilot agent 用它来定义专业角色）。

## Agentic Memory（重要！）

Copilot Memory 的机制对我的 memory 工具有直接参考价值：

### 核心机制
1. **28天自动过期** — 防止知识过时
2. **引用校验** — 记忆附带源码位置，使用前校验是否还准确
3. **延期机制** — 被使用过的记忆会延期
4. **仓库级别共享** — 团队共享，不是用户私有

### 我的 memory 工具差距
- ❌ 没有过期机制（所有记忆永久存在）
- ❌ 没有引用校验（记忆可能过时）
- ❌ 没有使用追踪（不知道哪些知识被真正用到过）

### 改进方向
考虑在 memory 内容里加入"最后验证时间"字段，定期提醒用户哪些记忆可能已经过时。

## 快速参考链接
- Custom Agents: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-custom-agents
- Agent Skills: https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
- Agentic Memory: https://docs.github.com/en/copilot/concepts/agents/copilot-memory
- Agent Skills Spec: https://github.com/agentskills/agentskills
- Anthropic Skills (参考): https://github.com/anthropics/skills
