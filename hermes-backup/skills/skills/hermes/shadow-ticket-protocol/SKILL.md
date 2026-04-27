---
name: shadow-ticket-protocol
description: Hermes DM 场景下的影子工单协议——当主 Agent 无法直接调度独立专业 Agent 时，通过手动路由 + 影子追踪实现最佳任务闭环。V2.1-Patch-Final。
tags: [workflow, delegation, hermes, dm, checkpoint]
---

# Shadow Ticket Protocol (V2.1-Patch-Final)

## 触发场景
在 DM（私聊）中收到专属领域任务时（VPS/健康/游戏/研究），主 Agent 无法直接调度对应专业 Agent（联邦架构下同级独立），采用"手动路由 + 影子追踪"实现最佳闭环。

## 核心原则（三条）

### ① 意图拦截（Intercept）
- 识别领域归属：VPS→老V / 健康→小健 / 游戏→小策 / 研究→小研
- **禁止**：派发匿名 sub-agent 执行该任务，或模拟对方 Agent 回答
- 输出：告知用户目标群组 + 执行经验预检

### ② 经验预检（Knowledge Pre-check）
- 在引导用户去对应群之前，先执行：
  `grep -i <关键词> ~/.hermes/global_knowledge.md`
- 若有匹配：提取核心解决方案，作为用户向目标 Agent 发起任务的参考背景一并告知
- 若无匹配：直接路由，不卡壳

### ③ 影子追踪（Shadow Tracking）
- 在 checkpoint 的 `active_sub_agents` 中写入：
  ```json
  {
    "task_id": "<自动生成>",
    "goal": "<任务描述>",
    "status": "wait_user_trigger",
    "assignee": "<Agent名>",
    "started_at": "<时间戳>"
  }
  ```
- 闭环判定：Session Reset 或 DM 触发下一轮对话时，扫描 `wait_user_trigger` 记录
- 主动询问："你之前要找 <Agent> 处理的事，处理完了吗？回复 Done 闭环，Pending 继续保留。"
- 用户回复 Done → 更新 status 为 done
- 用户回复 Pending → 继续保留

## active_sub_agents 数组格式
status 可选值：
- `running` — sub-agent 执行中
- `done` — 正常完成
- `failed` — 执行失败
- `failed_timeout` — 超时强制终止（须丢弃结果）
- `zombie_killed` — 被强制终止
- `wait_user_trigger` — 影子工单，等待用户触发闭环

## 关键约束
- 不尝试调度独立 Agent（联邦架构下无法跨 Agent 通信）
- 不模拟对方 Agent 回答专业问题
- 路由前必须先做经验预检（Knowledge Pre-check）

## 来源
Hermes V2.1-Patch-Final 协议，2026-04-26 与用户和 Gemini 协作迭代完成
