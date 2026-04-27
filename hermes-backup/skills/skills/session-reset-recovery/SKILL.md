---
name: session-reset-recovery
description: Session Reset 恢复指南 — 如何在上下文达到 204K tokens 自动重置后快速恢复任务。包括内置通知机制说明、P0 内存格式规范、Sync_Status skill 使用方法。
category: productivity
---
# Session Reset 恢复指南

## 背景
Hermes 在上下文达到 204K tokens 时会自动重置会话（Session Reset），对话历史清零，但 Memory 持久化存储不受影响。

## 核心认知

### Hermes 内置通知机制
Session Reset 后，Hermes **会自动发送飞书通知**（在下一次用户发消息时触发），内容：
```
◐ Session automatically reset (inactive for 24h). Conversation history cleared.
Use /resume to browse and restore a previous session.
```

**条件：**
- `policy.notify = True`（默认开启）
- `had_activity = True`（会话之前有活动）
- 飞书不在 `notify_exclude_platforms` 列表

Hermes 已有通知，**P1（外部启动脚本）价值有限**，真正核心是 P0 + P2。

## P0 — Memory 写入格式（多步骤任务必须遵守）

### 触发时机：每完成一个 meaningful step 立即写入，不是"快 reset 了才写"

多步骤任务从第一步起，**每个步骤完成后立即写 checkpoint**，不依赖上下文剩余量判断。

```json
{
  "task": "任务名",
  "step": 2,
  "status": "completed",
  "next_action": "下一步做什么",
  "timestamp": "2026-04-20 13:00"
}
```

同时写入 `~/.hermes/task_checkpoint.json`（P0 规范要求双写）。

**效果：** Reset 后能通过 Memory 快速看懂任务进度，而不是读模糊的文字摘要。

### ⚠️ 常见错误（已踩坑）
- ❌ "等感觉快 reset 了再写" → context 涨得快，经常还没写就 reset 了，任务进度丢失
- ✅ "每完成一步立即写" → reset 发生在任何时机，下个 session 都能从上一个成功步骤继续

## P2 — Sync_Status Skill

**触发词：** `/resume`、`继续上一个任务`、`从刚才的地方继续`

**执行流程：**
1. 读 Memory 最近一条 JSON 状态
2. 生成自然语言上下文摘要，注入 LLM
3. 继续执行 `next_action`
4. 完成后更新 Memory

**Skill 位置：** `skills/productivity/sync-status/SKILL.md`

## OpenClaw 清理记录

以下内容已从 Hermes 中清理：

### 已删除
- `~/.hermes/migration/openclaw/` — 旧迁移数据
- `~/.hermes/skills/openclaw-imports/` — 旧 skill（含 learn-me、self-improving-agent 等）

### 已修改
- `skills/autonomous-ai-agents/hermes-agent/SKILL.md` — 移除 OpenClaw 竞品引用
- `skills/hermes-feishu-troubleshooting/SKILL.md` — 移除 openclaw 迁移路径引用
- `skills/social-media/xurl/SKILL.md` — 移除 openclaw upstream 来源
- `skills/creative/popular-web-designs/templates/ollama.md` — 示例标签替换
- `skills/creative/baoyu-infographic/PORT_NOTES.md` — 迁移记录修复

## 图片理解工具

**MiniMax 模型不支持 `vision_analyze`**，使用 `mcp_minimax_plan_understand_image` 代替：
```python
mcp_minimax_plan_understand_image(image_source="图片路径", prompt="描述要求")
```

## 恢复任务上下文 — 快速上手流程

当被问"情况如何了"、"在做什么"、"还好吗"等模糊状态查询时，**先不搜关键词**，直接走：

```
session_search(limit=3)  # 无参数 → 最近会话列表
```

看 `last_active` 和 `message_count`：
- `last_active` 最近 + `message_count` 大的 = 活跃 session
- 有 checkpoint 文件的优先读 `~/.hermes/task_checkpoint.json`

**避免：** 一上来就用关键词搜索（会漏掉没命中关键词的活跃 session，白耗调用次数）。

---

### 找「今天」特定短语时 session_search 失效的处理

**症状：** 用户说「去找今天的聊天记录，最后消息是 xxx」，但 `session_search` 搜不到。

**根因：** `session_search` 依赖 FTS 索引，某些新 session（刚归档或还在活跃的）可能未被索引；短语可能出现在当前 session 自身（用户刚发的消息），造成「搜到了但其实在搜自己」的假象。

**处理步骤（按顺序）：**

```bash
# 1. 先确认当前 session 文件里是否已经有这条消息（避免搜自己）
grep "目标短语" ~/.hermes/sessions/当前session文件名.jsonl

# 2. 直接 grep 今天的所有 session 文件
grep "目标短语" ~/.hermes/sessions/20260425_0*.jsonl

# 3. 都没有 → 说明消息在「上一个 session 结尾 → 新 session 开始」的空档
#    即：上一个 session 在发这条消息之前就 reset 了
```

**关键文件时间戳参考（2026-04-25）：**
```
08:20  当前 session（69334 bytes）
08:03  074631
07:43  071344
07:09  063518
06:32  060140
06:00  053102
05:27  040511
04:01  035341
03:51  164411
03:46  034653
03:40  164930（4月24日的 session）
```

**原则：** 找「今天的某句话」→ 直接 grep 当天 session 文件 > session_search。session_search 适合模糊回顾，不适合定位精确短语。

## 优先级总结

| 优先级 | 动作 | 说明 |
|--------|------|------|
| P0 ✅ | JSON Memory 格式 | 立即执行，Reset 后能看懂任务 |
| P2 ✅ | Sync_Status Skill | /resume 时自动续接，已创建 |
| P1 ⚠️ | 启动通知脚本 | 锦上添花，Hermes 内置通知已覆盖 |
