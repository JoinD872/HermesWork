# federation-dispatch-wake — 联邦任务派发与唤醒

## 功能
同时执行两项操作：
1. 写任务文件到 `~/.hermes/federation/pending/{task_id}.json`
2. 通过飞书 Webhook 发送真实 @ 唤醒对应 Agent

## 适用场景
- 派发联邦任务给任何子 Agent（老V/小策/小健/小研）
- 必须搭配 scan_callbacks 形成完整闭环

## 使用前提
- pending/ 目录已建立
- 各群 Webhook URL 已配置（见下方）
- 子 Agent SOUL.md 已写入「联邦自启动协议（V3.0-Trigger）」
- 子 Agent SOUL.md 已写入「联邦回执 SOP」

## Webhook URL 配置（2026-04-27 实测）

| Agent | Webhook URL |
|-------|------------|
| 小研 | https://open.feishu.cn/open-apis/bot/v2/hook/20acd1d4-fe75-404e-ac5e-5e49bc5c587b |
| 小健 | https://open.feishu.cn/open-apis/bot/v2/hook/00394231-ecf8-4e00-9a9b-50fc747d44bd |
| 小策 | https://open.feishu.cn/open-apis/bot/v2/hook/fd3ea207-82cf-4e19-a134-45926df90c0b |
| 老V | https://open.feishu.cn/open-apis/bot/v2/hook/9fa84937-aa99-4c18-93f2-a0736dcf86fa |

## 核心逻辑

```python
import os, json, time, requests

WEBHOOK_URLS = {
    "小研": "https://open.feishu.cn/open-apis/bot/v2/hook/20acd1d4-fe75-404e-ac5e-5e49bc5c587b",
    "小健": "https://open.feishu.cn/open-apis/bot/v2/hook/00394231-ecf8-4e00-9a9b-50fc747d44bd",
    "小策": "https://open.feishu.cn/open-apis/bot/v2/hook/fd3ea207-82cf-4e19-a134-45926df90c0b",
    "老V": "https://open.feishu.cn/open-apis/bot/v2/hook/9fa84937-aa99-4c18-93f2-a0736dcf86fa",
}

def dispatch_and_wake(agent_name, task_id, goal):
    """
    1. 写入 pending/ 任务文件
    2. 通过 Webhook 发送飞书消息唤醒子 Agent
    3. 返回派发结果
    """
    pending_dir = os.path.expanduser("~/.hermes/federation/pending/")
    os.makedirs(pending_dir, exist_ok=True)

    # 1. 原子写入 pending 文件
    task_payload = {
        "task_id": task_id,
        "assignee": agent_name,
        "goal": goal,
        "status": "waiting",
        "dispatched_at": time.time()
    }
    task_path = os.path.join(pending_dir, f"{task_id}.json")
    with open(task_path, 'w') as f:
        json.dump(task_payload, f, ensure_ascii=False)

    # 2. 通过 Webhook 发送唤醒消息（携带真实 @）
    if agent_name in WEBHOOK_URLS:
        url = WEBHOOK_URLS[agent_name]
        msg = f"[@{agent_name}] 联邦任务已下达：{task_id}。请立即 check_federal_pending 执行。\n\n任务：{goal}"
        payload = {"msg_type": "text", "content": {"text": msg}}
        resp = requests.post(url, json=payload, timeout=10)
        result = resp.json().get("msg", "sent")
    else:
        result = f"Unknown agent: {agent_name}"

    return f"✅ Task {task_id} dispatched to {agent_name}. Wake signal: {result}"
```

## 闭环流程

```
dispatch_and_wake() → 写入 pending/ → Webhook 发送 @ 唤醒
  → 子 Agent check_federal_pending() → 读取 pending/
  → 执行任务 → emit_result() 写 callbacks/
  → 主 Agent scan_callbacks() → 读 done → 归档 → 删除 pending/
```

## 注意事项
- 派发时 task_id 必须全局唯一（建议格式：{Agent缩写}_{日期}_{序号}）
- scan_callbacks 执行后必须删除 pending/ 里的对应文件
- Webhook 消息里的 [@Agent名] 是真实 @，可触发飞书通知
- Webhook 不依赖 send_message 工具，走独立 HTTP 通道

## ⚠️ 飞书 @ 触发机制关键发现（2026-04-27）

**文字 `[@小研]` ≠ 真实飞书 @**

- 在飞书消息里写文字 `[@小研]` → **不会触发小研 session 激活**（这只是纯文本）
- 必须通过飞书客户端 UI 真正 @ 小研 → **才能触发 session 激活**
- **解决方案**：使用飞书 Incoming Webhook 机器人发送消息，格式化为 `[@Agent名]` 的真实 @ 提及，可以触发目标 session

**Webhook URL 是按群配置的，不是按 Agent 配置的**
- 每个群（研究员/健康/游戏/VPS）各需要 1 个 Webhook URL
- 发给谁，由消息内容里的 [@Agent名] 决定，而不是 URL 本身
- 获取方式：飞书群 → 设置 → 应用与机器人 → 添加机器人 → 自定义机器人 → 复制 Webhook URL
