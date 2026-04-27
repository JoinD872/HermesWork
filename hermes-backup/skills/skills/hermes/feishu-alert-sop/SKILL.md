---
name: feishu-alert-sop
description: 飞书告警 SOP — 强制携带阻断原因 + 备选方案的格式化通知模板
category: hermes
---

# 飞书告警 SOP

## 目的

收到报错/任务失败时，发出的飞书告警不应只有"报错了"，要带 **Plan B**，让用户不需要再追问就能决定下一步。

## 强制字段模板

```
🚨 任务中断 | <任务名>
❌ 阻断原因：<Current_Blocking_Issue>
🔁 备选方向：<Hypothetical_Next_Step>
⏱ 已尝试：<重试次数> 次 / <耗时>
```

## 填写规则

| 字段 | 填写要求 |
|------|---------|
| `阻断原因` | 一句话说明白卡在哪，不需要完整日志 |
| `备选方向` | **不需要深度推理**，给一个直觉层面的"换个方向试试"即可 |
| `已尝试` | 填次数和耗时，没有就写"未重试" |

## 何时触发

- cron 任务执行失败/超时
- sub-agent 返回错误，主控判断无法自动恢复
- 重启 Gateway 后的状态通知
- 任何需要用户介入才能继续的情况

## 例外

- 简单的一句话说清楚的不需要套模板（如"重启 Gateway 成功，已生效"）
- 用户明确说"先不管了" → 不发告警

## 坑（2026-04-26 验证）

- send_message 发飞书必须加 `feishu:` 前缀，否则报 `Unknown platform`
  - 错误：`target="oc_xxx"`
  - 正确：`target="feishu:oc_xxx"`
- DM 目标（`oc_8391fa2b38acbd759ff75ab3616d5d1f`）通常走 cron auto-delivery，不需要额外 send_message
