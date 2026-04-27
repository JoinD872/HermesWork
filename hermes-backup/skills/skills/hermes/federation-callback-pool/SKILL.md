---
name: federation-callback-pool
description: Hermes 联邦任务派发与闭环机制 V3.0.1-FINAL — 通过文件系统（pending/callbacks）中转，绕过 Session 隔离，支持原子化标记、超时重置、结果归口
tags: [federation, multi-agent, cron, task-dispatch, v3.0.1]
category: hermes
---

# 联邦任务派发与闭环机制（V3.0.1-FINAL）

## 问题背景
主 Agent 发消息给子 Agent 后，子 Agent 的回复在其独立 session 里，主 Agent 收不到。任务闭环依赖用户中间人。

## 解决方案
通过共享文件系统作为物理中转介质，绕过飞书 Session 隔离：
- `pending/` — 主 Agent 写入待执行任务
- `callbacks/` — 子 Agent 写入执行结果
- 主 Agent 扫描 `callbacks/` 验证闭环

## ⚠️ V3.0.1-FINAL 三条军规（严禁违反）

1. **原子性第一**：必须先写 `status: "processing"` + `locked_at: Unix Epoch`，再执行任何逻辑
2. **Unix Epoch 唯一性**：全系统所有时间字段只用 `int(time.time())`，严禁 strftime/ISO
3. **结果归口**：`emit_result()` 是唯一任务终结手段，未调用前严禁在群里回复「Done」

## 任务状态机

```
waiting → (扫描到) → processing → (完成) → done
                         ↑
              (超时30min自动重置为waiting)
```

## 目录结构

```
~/.hermes/federation/
├── callbacks/          # 回执池（已完成任务）
│   └── {task_id}.json
├── callbacks/archive/  # 已处理归档
└── pending/            # 任务队列（待处理任务）
    └── {task_id}.json
```

## Pending 文件格式

```json
{
  "task_id": "TASK_001",
  "assignee": "老V",
  "goal": "查询内存使用率",
  "status": "waiting",
  "dispatched_at": 1777263429
}
```

## 回执文件格式

```json
{
  "task_id": "TASK_001",
  "assignee": "老V",
  "status": "done",
  "payload": {
    "summary": "核心结论（300字以内，严禁塞原始Log）",
    "key_findings": [],
    "action_items": []
  },
  "completed_at": 1777263500
}
```

## 心跳超时重置（防止僵尸任务死锁）

每次扫描 pending 前先执行：

```python
if task.get('status') == 'processing':
    age_minutes = (time.time() - task.get('locked_at', 0)) / 60
    if age_minutes > 30:
        task['status'] = 'waiting'
        task.pop('locked_at', None)
        with open(path, 'w') as f:
            json.dump(task, f)
```

## emit_result 标准实现（子 Agent 侧）

```python
def emit_result(task_id, summary):
    import os, json, uuid, time
    target_dir = os.path.expanduser("~/.hermes/federation/callbacks/")
    os.makedirs(target_dir, exist_ok=True)
    payload = {
        "task_id": task_id,
        "assignee": "<Agent名>",
        "status": "done",
        "payload": {
            "summary": summary,  # 300字以内
            "key_findings": [],  # 无内容则留空
            "action_items": []
        },
        "completed_at": int(time.time())  # Unix Epoch
    }
    temp_path = f"/tmp/{uuid.uuid4()}.json"
    final_path = os.path.join(target_dir, f"{task_id}.json")
    with open(temp_path, 'w') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.rename(temp_path, final_path)
    # 闭环即删除 pending 文件（严禁残留）
    pending_file = os.path.expanduser(f"~/.hermes/federation/pending/{task_id}.json")
    if os.path.exists(pending_file):
        os.remove(pending_file)
```

## scan_callbacks（主 Agent 侧）

```python
import os, json

def scan_callbacks():
    callback_dir = os.path.expanduser("~/.hermes/federation/callbacks/")
    archive_dir = os.path.expanduser("~/.hermes/federation/callbacks/archive/")
    os.makedirs(archive_dir, exist_ok=True)
    results = []
    for fname in os.listdir(callback_dir):
        if not fname.endswith('.json'):
            continue
        path = os.path.join(callback_dir, fname)
        with open(path) as f:
            data = json.load(f)
        if data.get("status") == "done":
            results.append({
                "task_id": data.get("task_id"),
                "summary": data.get("payload", {}).get("summary", ""),
                "completed_at": data.get("completed_at")
            })
            os.rename(path, os.path.join(archive_dir, fname))
    return results
```

## 主 Agent 派发任务

```python
import os, json, time
pending_dir = os.path.expanduser("~/.hermes/federation/pending/")
os.makedirs(pending_dir, exist_ok=True)
task = {
    "task_id": "TASK_001",
    "assignee": "老V",
    "goal": "查询内存使用率",
    "status": "waiting",
    "dispatched_at": int(time.time())
}
with open(os.path.join(pending_dir, "TASK_001.json"), 'w') as f:
    json.dump(task, f)
```

## 已知坑点（实战发现，2026-04-27）

| 坑 | 根因 | 解法 |
|----|------|------|
| Cron 不读 pending/ | prompt 写死读 `research_tasks.md` | 在 prompt 最前面插入 pending 扫描逻辑 |
| script 参数误用 | `export HERMES_HOME=...` 被当作脚本路径执行 | 清空 `script` 字段，用 `workdir` 代替 |
| pending 文件残留 | 状态改 done 后未删除 | 闭环后必须 `os.remove(pending_file)` |
| 僵尸任务死锁 | processing 状态卡住 | 心跳超时重置（30分钟自动重置） |
| 时间戳不统一 | ISO/Epoch 混用 | 统一 `int(time.time())` |

## Cron Job ID 速查（2026-04-27 实测）

| Agent | job_id | Schedule (UTC) | 本地 GMT+8 |
|-------|--------|----------------|------------|
| 老V | `a259819c24f4` | 09:00 | 17:00 |
| 小健 | `a2d3c2998db3` | 11:00 | 19:00 |
| 小研 | `ef20c63571f7` | 19:00 | 03:00 |
| 小策 | `5e3728b97221` | 21:00 | 05:00 |

## 验证结果（2026-04-27）

- 老V cron job（a259819c24f4）✅ 已接入 pending 机制，callback 写入验证通过
- 小研 cron job（ef20c63571f7）✅ 已接入 pending 机制，callback 写入验证通过
- 小健 cron job（a2d3c2998db3）✅ 新建，已接入 V3.0.1-FINAL 协议
- 小策 cron job（5e3728b97221）✅ 新建，已接入 V3.0.1-FINAL 协议
- 手动 `cronjob(action='run')` 可触发任务执行（callback 写入验证通过）

