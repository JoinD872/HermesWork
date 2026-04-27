---
name: multi-agent-config-sync
description: 多 Agent 配置同步与飞书群 chat_id 修复流程——当共享配置（如图片识别方式）需要同步到所有子 agent 群时的标准操作
tags: [feishu, multi-agent, chat-id, sync]
category: hermes
---

# 多 Agent 配置同步与 chat_id 修复流程

## 背景

Hermes 多 agent 部署中，各群 agent 是独立 session。更新共享 skill 文件后，**已有 session 不会自动重新加载**，需要主动在各群发消息通知。

## Step 1：确认所有 chat_id（容易出错！）

chat_id 分散在多处，**必须全部确认一致**：

| 文件 | 用途 |
|------|------|
| `~/.hermes/SOUL.md` | 路由规则 |
| `~/.hermes/profiles/<profile>/SOUL.md` | 各 profile 自己的 SOUL |
| `~/.hermes/skills/hermes/hermes-multi-agent-architecture/SKILL.md` | 多 agent 架构文档 |
| `~/.hermes/skills/feishu-*/SKILL.md` | 各飞书相关 skill |
| `~/.hermes/memories/MEMORY.md` | 记忆文件 |

**搜索所有旧 ID**：
```bash
grep -r "oc_357b06d7ecde7333a9200de609d4440c" ~/.hermes --include="*.md"
```

## Step 2：批量替换旧 chat_id

用 patch 的 `replace_all` 一次性换掉：
```python
patch(mode="replace", path=".../SKILL.md",
      old_string="oc_357b06d7ecde7333a9200de609d4440c",
      new_string="oc_5a883cbe523b1a93ee269bba2f8536a0",
      replace_all=True)
```

## Step 3：通知各群 agent

用 `send_message` 同时发往所有群：

```
目标群：
- 游戏制作组：oc_5a883cbe523b1a93ee269bba2f8536a0
- 健康助手群：oc_6dbf15aa718c29adca8d085017930a71
- 凌晨研究员：oc_ec9adb3139cd38ac706cd7a54c4d059d
```

**错误处理**：
- 若返回 `Bot/User can NOT be out of the chat` → chat_id 错误或 bot 未加入该群
- 先确认正确 ID，再补发

## Step 4：验证旧 ID 已全部清除

```bash
grep -r "<旧ID>" ~/.hermes --include="*.md"
# 期望：0 results
```

## 已知 chat_id（2026-04-25 确认）

| 群 | chat_id |
|---|---------|
| 游戏制作组（策划+UE5）| `oc_5a883cbe523b1a93ee269bba2f8536a0` |
| 健康助手群 | `oc_6dbf15aa718c29adca8d085017930a71` |
| 凌晨研究员 | `oc_ec9adb3139cd38ac706cd7a54c4d059d` |

## 教训

- chat_id 写错会导致 `send_message` 报 `Bot/User can NOT be out of the chat`
- 不要凭记忆写 chat_id，每次发消息前用 `search_files` 在 `~/.hermes` 里搜索确认
- 旧 ID 往往残留在多个文件里，修复时要全局搜索 + replace_all
