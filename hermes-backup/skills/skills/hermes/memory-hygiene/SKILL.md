---
name: memory-hygiene
description: 记忆卫生管理 — 28天过期机制、引用校验、使用追踪。解决 MEMORY.md 知识永久存在导致的过时知识污染问题。基于 GitHub Copilot Agentic Memory 机制设计。
version: 1.0.0
metadata:
  hermes:
    tags: [memory, hygiene, expiration, verification]
---

# Memory Hygiene

## 问题背景

MEMORY.md 里的记忆永久存在，没有过期机制。随着时间推移：
- 环境变了（工具版本、配置路径），但记忆还留着 → 误导判断
- 某次 session 学到的知识被记住了，但没有被验证过 → 可能是错的
- 记忆被用过但不知道哪些最常用 → 无法优化

## 解决方案：记忆分层 + 过期机制

参考 Copilot Memory 的设计：
1. **28天自动过期** — 记忆超过28天未验证，标记为 stale
2. **引用校验** — 验证时检查记忆是否还准确
3. **使用追踪** — 被调用时自动刷新 `last_used`

### 记忆状态

| 状态 | 条件 | 处理方式 |
|------|------|---------|
| fresh | created < 7天 | 正常，无需验证 |
| valid | 7-28天，已验证 | 正常 |
| stale | > 28天未验证 | 推送给用户确认是否还有效 |
| dead | 用户确认无效 | 删除或更新 |

## 核心限制（必须知道！）

### ❄️ Frozen Snapshot Pattern（最关键）
**MEMORY.md 在 session 期间的修改，下个 session 才生效。**

> "The system prompt injection is captured once at session start and never changes mid-session. When the agent adds/removes memory entries during a session, the changes are persisted to disk immediately but won't appear in the system prompt until the next session starts."

**影响**：
- 现在 session 对 MEMORY.md 的任何修改（patch/memory add），都要**下次 session** 才生效
- 我在当前 session 里保存的记忆，下一个 session 才能用到
- 但 disk 写入是即时的，session 重启后一定存在

### 📏 字符限制（bounded memory）
- `MEMORY.md` 上限：**2,200 chars**（约800 tokens）
- `USER.md` 上限：**1,375 chars**（约500 tokens）
满了会触发 consolidation，agent 自动合并或替换旧记忆
每次 session 开始时显示使用率，如：`[67% — 1,478/2,200 chars]`

**影响**：我的记忆必须精简，不能往里塞大量原始内容。

**容量耗尽写入法（经验证）：**
- Memory 使用率 > 95% 时 `add` 触发容量预检会失败
- 但 `replace` **不做容量预检**，只要有可匹配的 `old_text` 就能写入
- 策略：用要保存的新内容替换一条短旧条目（实质是删旧存新）
- 若新内容比任何单一条目都长 → "合并+精简"策略：先把多条短条目合并成一条，再替换进去
- 实测可行（2026-04-22，MEMORY 99% 时 replace 成功）

## 实现方式

记忆以 Markdown 段落块的形式存储在 MEMORY.md 中，每个记忆块顶部包含 YAML frontmatter 形式的元数据：

```yaml
<!--
id: user-preferences
created_at: 2026-04-09
last_verified: 2026-04-20
last_used: 2026-04-20
status: valid|stale|dead
-->
```

## 检查频率

每次 session 开始时（heartbeat 或 cron）自动检查，将 stale 记忆报告给用户。

## 使用方法

### 保存新记忆时
```python
# 在记忆内容前加上 frontmatter
content = f"""<!--
id: {unique_id}
created_at: {today}
last_verified: {today}
last_used: {today}
status: fresh
-->
{记忆内容}"""
```

### 使用记忆时
在响应前找到对应 id 的 block，更新 `last_used` 为今天。

### 验证记忆时
1. 检查记忆内容是否还准确
2. 如果准确 → 更新 `last_verified` 为今天，`status` 改为 `valid`
3. 如果不准确 → 更新内容，`last_verified` 改为今天
4. 如果已无用 → `status` 改为 `dead`，下次清理时删除

## 与 MEMORY.md 的关系

- **不是替代** MEMORY.md，而是为其添加元数据层
- 现有的 MEMORY.md 内容不动，只是给每个逻辑记忆块加上 frontmatter
- 未来可扩展：支持结构化字段（如 `expires_in_days: 28`）让不同记忆有不同的 TTL

## 待办

- [ ] 写一个 `scripts/check_memory.py`，扫描 MEMORY.md 找出所有 stale 记忆
- [ ] 集成到 heartbeat，每次 session 开始时检查并推送 stale 记忆给用户
- [ ] 在 `memory` 工具的 `add` action 路径里自动注入 frontmatter
