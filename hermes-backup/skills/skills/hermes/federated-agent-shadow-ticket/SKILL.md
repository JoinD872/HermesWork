---
name: federated-agent-shadow-ticket
description: 联邦 Agent 影子工单协议 — 在多 Agent 独立部署、无法直接通信的架构下，实现跨域任务的拦截、预检、追踪与闭环。用户作为高保真数据链路桥接各 Agent。
tags: [hermes, multi-agent, workflow, delegation]
sources:
  - Hermes V2.1-Patch-Final 规范（MEMORY.md, 2026-04-26）
  - 演化自 Gemini 驱动的多轮架构迭代
---

# Federated Agent Shadow Ticket Protocol
联邦 Agent 影子工单协议 — V2.1-Patch-Final

## 背景与问题
在 Hermes 多 Agent 联邦架构下，各 Agent（老V/小策/小健/小研）运行在独立的 context 和环境中，主 Agent 无法直接调度或接收其他 Agent 的回调。当用户在 DM 询问专属领域问题时，存在两个核心矛盾：
1. 主 Agent 不能直接回答（越权/不专业）
2. 主 Agent 无法自动调度目标 Agent（物理隔离）

## 核心解法：影子工单协议（四条）

### ① 意图拦截（Intercept）
识别领域关键词，禁止派发匿名 sub-agent 执行，禁止模拟目标 Agent 回答。
专属领域归属：
| 关键词 | 目标 Agent | 飞书群 |
|--------|-----------|--------|
| VPS/网络/隧道/Docker | 老V | oc_cc9c |
| 健康/身体/胃/颈椎 | 小健 | oc_6dbf |
| 游戏/UE5/策划 | 小策 | oc_5a883c |
| AI/ML/研究/论文 | 小研 | oc_ec9a |

### ② 经验预检（Knowledge Pre-check）
路由前先执行：
```bash
grep -i <关键词> ~/.hermes/global_knowledge.md
```
- 有匹配：提取坑点和解决方案，作为用户向目标 Agent 的参考背景
- 无匹配：直接路由

### ③ 影子追踪（Shadow Tracking）
在 checkpoint 的 `active_sub_agents` 中写入：
```json
{
  "task_id": "TICKET_<Unix TS>",
  "goal": "<任务描述>",
  "status": "wait_user_trigger",
  "assignee": "<Agent名>",
  "started_at": "<ISO时间>"
}
```

### ④ 跨 Agent 背景打包（Sync-Patch）（补充条款）
自动生成以下格式文本块，用户复制到目标群 @ 对应 Agent：
```
[联邦背景同步]：基于 MEMORY.md V2.1 规范
- 历史关联坑点：<从 global_knowledge.md 提取的核心关键词>
- 预检建议方案：<建议目标 Agent 优先尝试的操作>
```

### 主动闭环判定
Session Reset 或下轮 DM 对话时：
1. 扫描 `active_sub_agents` 中 `status == wait_user_trigger` 的记录
2. 主动询问："{Agent} 那件事处理完了吗？回复 Done 闭环，Pending 保留。"
3. Done → status: done；Pending → 保留

## active_sub_agents status 枚举
`running / done / failed / failed_timeout / zombie_killed / wait_user_trigger`

## 关键教训（坑点）

### 坑点 1：主动调度思路不可行
- 尝试：主 Agent 直接调度其他 Agent
- 失败原因：联邦 Agent 间无物理通信链路，各 Agent 独立部署
- 解决：改用"用户作为桥接"的 Sync-Patch 方案

### 坑点 2：Ticket 记录格式过度设计
- 尝试：建立独立的 TICKET 数据结构
- 问题：增加复杂度，与现有 checkpoint 不兼容
- 解决：复用 active_sub_agents，status 扩展含 wait_user_trigger

## 适用条件
- 多 Agent 联邦架构（独立部署、独立 context）
- 主 Agent 需处理跨领域任务但无权直接执行
- Agent 间无共享数据库或通信信道

## 相关文件
- `~/.hermes/memories/MEMORY.md`：V2.1 工作流规范（含完整协议）
- `~/.hermes/global_knowledge.md`：跨 Agent 坑点共享库
- `~/.hermes/task_checkpoint.json`：影子工单记录位置
