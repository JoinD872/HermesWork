---
name: sync-status
description: Sync status — Resume a task from the last checkpoint. Triggered when user says /resume or asks to continue from where left off. Reads the last JSON checkpoint from memory and continues the task.
category: productivity
---
# Sync Status — 断点续传

## 触发条件
用户说 `/resume`，或者要求"继续上一个任务"、"从刚才的地方继续"。

## 执行流程

### 1. 读取 Memory 中最近一条 JSON 状态
从 Memory 读取最近的 `{"task": ..., "step": ..., "status": ..., "next_action": ..., "timestamp": ...}` 格式数据。

### 2. 解析状态
- `task`：任务名称
- `step`：已完成的步骤编号
- `status`：completed / in_progress
- `next_action`：下一步要做什么
- `timestamp`：时间戳

### 3. 生成上下文摘要
用 LLM 阅读 JSON 内容，生成一段自然语言摘要，格式示例：

> "上一个任务：[配置学习计划]，已完成第 2 步（生成早间问候语），下一步是：生成晚间总结。请继续执行。"

### 4. 注入上下文继续执行
将摘要作为 system context 注入，继续执行 `next_action`。

### 5. 完成后更新 Memory
任务真正完成后，写入最终状态：
```json
{
  "task": "[任务名]",
  "step": N,
  "status": "completed",
  "next_action": "none",
  "timestamp": "YYYY-MM-DD HH:MM"
}
```

## 错误处理
- 若 Memory 中无 JSON 状态，回复用户："没有找到上一次的进度记录，请告诉我你想继续什么任务。"
- 若 JSON 格式异常，同样告知用户并请其描述任务。

## 注意事项
- Sync_Status 触发后，后续步骤仍遵循 P0 规范（每步写 Memory）
- 绝对不让用户手动描述进度——这是 Sync_Status 的核心价值
