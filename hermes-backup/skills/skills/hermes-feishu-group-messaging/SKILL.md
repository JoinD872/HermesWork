---
name: hermes-feishu-group-messaging
description: Hermes 飞书群发消息规范 — target 格式、可用目标列表、已知坑点
version: 2026-04-26
tags: [feishu, messaging, federation]
---

# Hermes 飞书群发消息规范

## 群发消息 target 格式

**必须用群名，不要用原始 ID。**

```
✅ 正确：feishu:研究员 / feishu:VPS技术助手-老V / feishu:游戏制作组
❌ 错误：feishu:oc_ec9adb3139cd38ac706cd7a54c4d059d
```

**原因**：工具内部 API 构造时，群名会自动映射到 `receive_id_type=chat_id`，而原始 ID 会触发 P2P 格式校验导致报错 `invalid receive_id`。

## 可用目标（2026-04-26 验证）

| 群名 | target 格式 |
|------|------------|
| DM（当前用户） | `feishu:oc_8391fa2b38acbd759ff75ab3616d5d1f` |
| 研究员群 | `feishu:研究员` |
| 健康助手群 | `feishu:健康助手` |
| 游戏制作组 | `feishu:游戏制作组` |
| VPS技术助手-老V | `feishu:VPS技术助手-老V` |

## 查询方式

```
send_message(action='list')
```

## 已知坑点

- bot 必须已加入目标群才能发送，否则报错
- 原始 ID 格式在群发场景下报 `invalid receive_id`，用群名绕过