---
name: federation-result-beautifier
description: 联邦任务结果美化 — 将 callbacks/ 的 JSON 格式化为易读的飞书报告，包含 emoji 状态 + 表格 + 分级结论
tags: [federation, report, result, beautify]
category: hermes
---

# 联邦任务结果美化报告

## 触发条件

当需要向用户汇报联邦任务完成结果时，自动套用此格式。

## 输入

`~/.hermes/federation/callbacks/*.json` 中的任意已完成的 task 文件。

## 报告模板

```
## {emoji} {Agent名字} — {task_id}
**任务**：{goal 原文}

**结论**：{summary 提炼}

### 关键发现
{key_findings 转表格或列表}

### 待办
{action_items 转列表（若无则写「无」）}

⏱ {completed_at 从 Unix Epoch 转换为本地时间}
```

## Agent emoji 映射

| Agent | emoji |
|-------|-------|
| 老V | 🖥️ |
| 小研 | 🌙 |
| 小健 | 💪 |
| 小策 | 🎮 |

## 时间转换

`completed_at` 是 Unix Epoch（整数），需要转换为本地时间：
- Epoch ÷ 1000 → 若是毫秒级则需处理
- 转换：`datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M")` + " GMT+8"

## 状态判断

- `status == "done"` → ✅ 完成
- `status == "processing"` → 🔄 进行中
- `status == "failed"` → ❌ 失败

## 注意事项

- summary 必须保留核心结论，不得删改原意
- key_findings 如果是空数组，报告里写「无」
- action_items 如果是空数组，报告里写「无待办」
- 数字必须带单位（GiB / MB / % 等）
- 严禁将原始 JSON 直接发给用户
