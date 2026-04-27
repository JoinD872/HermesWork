---
name: hermes-internals
description: Hermes Agent 内部机制核心知识 — 基于官方文档。Frozen Snapshot Pattern、字符限制、Skills 三级加载、OpenClaw 迁移。
version: 1.0.0
metadata:
  hermes:
    tags: [hermes, internals, memory, skills, openclaw, migration]
---

# Hermes Internals

## ❄️ Frozen Snapshot Pattern（最重要）

**Session 期间对 MEMORY.md 的修改，下个 session 才生效。**

> "The system prompt injection is captured once at session start and never changes mid-session. When the agent adds/removes memory entries during a session, the changes are persisted to disk immediately but won't appear in the system prompt until the next session starts."

**实际影响**：
- `memory` 工具的 add/replace 操作 → disk 立即写入，下次 session 生效
- 我现在 session 里更新的记忆，刷新页面/重连后才能在 prompt 里看到
- 每次 session 开始时 prompt 里显示的 `%` 利用率是**上个 session 结束时**的快照

## 📏 Memory 字符限制（bounded memory）

- `MEMORY.md` 上限：**2,200 chars**
- `USER.md` 上限：**1,375 chars**
- 满了会自动 consolidation（合并/替换旧记忆）
- 当前利用率在每次 session 启动时显示，如：`[67% — 1,478/2,200 chars]`

**记忆必须精简**，不能往里塞大量原始内容。

## 📚 Skills 三级加载（Progressive Disclosure）

```
Level 0: skills_list() → [{name, description, category}, ...] (~3k tokens)
Level 1: skill_view(name) → 完整内容 + metadata（实际使用时才加载）
Level 2: skill_view(name, path) → 具体引用文件（最细粒度）
```

agent 调用 skill 时按需加载，不是全量加载。

## 🆕 Skills 新字段（我的 skills 缺的）

SKILL.md 支持但我目前没用到的字段：

```yaml
platforms: [macos, linux]        # OS 限制
metadata:
  hermes:
    fallback_for_toolsets: [web]  # 条件激活
    requires_toolsets: [terminal]  # 依赖条件
    config:                        # 安装时用户配置
      - key: my.setting
        description: "..."
        default: "value"
        prompt: "Prompt for setup"
```

## 🗂️ OpenClaw 迁移状态

**重要发现**：OpenClaw workspace 文件夹没有自动迁移。

```
OpenClaw 旧数据:  ~/.openclaw/workspace/knowledge/
  deep-learning.md   ← 还在这里！
  network.md         ← 还在这里！

Hermes skills:      ~/.hermes/skills/knowledge/  ← 不存在，未迁移
```

如果要从 OpenClaw 迁移 knowledge 文件，需要手动复制到 `~/.hermes/skills/`。

迁移命令 `hermes claw migrate` 只迁移人格/记忆/技能/消息配置/凭据，不迁移 workspace 普通文件。

## 🖼️ 截图 Vision 识别（重要认知纠正）

**`mcp_minimax_plan_understand_image` 不是 Hermes 内置 vision 工具**
- 它是 MiniMax Token Plan 的 IDE 插件（MCP server：`minimax-coding-plan-mcp`）
- 只能在 Claude Code / Cursor / OpenCode 等 IDE 中通过 MCP 调用
- 但在 Hermes Agent 环境下通过 `mcp_minimax_plan_understand_image` 调用**同样可用的**（MCP 已配置）

**Hermes 内置的 vision 工具**：
- `vision_analyze`：已禁用（`auxiliary.vision.provider` 设为空）
- `browser_vision`：需要在 browser 工具里有打开的页面，不能直接读本地 JPEG

**实际可用方案（按可靠性排序）**：
1. ✅ `mcp_minimax_plan_understand_image`：MCP 已配置，直接用，支持本地路径和 URL
2. 让用户直接粘贴文字描述截图内容
3. `browser_vision`：如果有打开的浏览器页面可用

**有效文件判断**：`file /root/.hermes/image_cache/img_xxx.jpg` 返回有效 JPEG（文件本身没坏）

## 🔄 SOUL.md / Profile 配置热重载限制

SOUL.md 和 profile 配置的修改，**只在新 session 启动时生效**。现有的活跃 session 不会热重载任何配置文件。

**实际影响**：
- 修改了 sub-agent 的 SOUL.md → 需要等那个 session 结束/Reset 才生效
- sub-agent 不响应新规则 → 因为它在用旧 session，旧的 SOUL.md 还在内存里
- **没有"通知运行中的 sub-agent 重载配置"的命令**，只能 Reset session

## ⚠️ Gateway 重启防翻车规则（P0，必须遵守）

涉及 Gateway 重启的任务，严格按以下顺序执行：

1. **写 checkpoint** → `~/.hermes/task_checkpoint.json`，记录任务状态 + 当前步骤 + 下一步 + 已有的 patch 改动
2. **记录改动** → 待执行的代码改动内容写入 checkpoint
3. **执行重启**
4. **重启后飞书通知** → "✅ Gateway 已重启，任务状态：..."
5. **重启后恢复** → 先读 checkpoint，确认改动是否生效，再继续任务

Gateway 在 TTY 前台运行时是 session leader，`kill` 命令会把自己也带走。正确做法是用 screen/tmux 托管，或先确认没有旧进程再重启。

## 快速参考链接
- 官方文档：https://hermes-agent.nousresearch.com/docs
- 中文文档：https://hermes.xaapi.ai
- 中文社区 FAQ：https://hermesagent.org.cn/docs/reference/faq
- agentskills.io 规范：https://agentskills.io/specification
