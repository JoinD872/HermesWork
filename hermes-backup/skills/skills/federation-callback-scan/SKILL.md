---
name: federation-callback-scan
description: 联邦回执池 — 通过磁盘文件实现跨 Agent 任务闭环，包含 pending/callbacks/ 目录管理、Cron Job 与 Federation 协议断连的坑点记录
tags: [federation, cron, multi-agent, callback]
category: hermes
---

# Federation Callback Pool — 联邦回执池 V2.3

## 核心问题（为什么需要这个架构）
主 Agent 发消息给子 Agent 后，子 Agent 的回复存在于各自独立 session，主 Agent 收不到。
任务闭环依赖用户中间人做传话筒。

## 解决方案：磁盘文件做中转
```
子 Agent 执行 emit_result() → 写入 ~/.hermes/federation/callbacks/{task_id}.json
                                                    ↓
                        主 Agent 每次唤醒时 scan_callbacks() 扫描
                                                    ↓
                        提取 payload.summary → 归档至 archive/ → 删除 pending/
```

## 目录结构
```
~/.hermes/federation/
  callbacks/          # 回执池（已完成任务）
    archive/          # 已处理归档
  pending/            # 任务队列（新派发待处理）
```

## 回执文件标准格式
```json
{
  "task_id": "T001",
  "assignee": "小研",
  "status": "done",
  "payload": {
    "summary": "300字内干货",
    "key_findings": [],
    "action_items": []
  },
  "completed_at": "2026-04-26T15:00:00Z"
}
```

## emit_result() 函数（子 Agent 端）
```python
def emit_result(task_id, summary):
    import os, json, uuid, time
    target_dir = os.path.expanduser("~/.hermes/federation/callbacks/")
    os.makedirs(target_dir, exist_ok=True)
    payload = {
        "task_id": task_id,
        "assignee": "小研",  # 替换为实际 Agent 名
        "status": "done",
        "payload": {
            "summary": summary,
            "key_findings": [],
            "action_items": []
        },
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    temp_path = f"/tmp/{uuid.uuid4()}.json"
    final_path = os.path.join(target_dir, f"{task_id}.json")
    with open(temp_path, 'w') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.rename(temp_path, final_path)  # 原子移动
```

## scan_callbacks() 函数（主 Agent 端）
```python
def scan_callbacks():
    import os, json, glob
    callback_dir = os.path.expanduser("~/.hermes/federation/callbacks/")
    archive_dir = os.path.expanduser("~/.hermes/federation/callbacks/archive/")
    os.makedirs(archive_dir, exist_ok=True)

    results = []
    for f in glob.glob(os.path.join(callback_dir, "*.json")):
        with open(f) as fp:
            data = json.load(fp)
        if data.get("status") == "done":
            results.append({
                "task_id": data.get("task_id"),
                "summary": data.get("payload", {}).get("summary", ""),
                "completed_at": data.get("completed_at")
            })
            os.rename(f, os.path.join(archive_dir, os.path.basename(f)))
    return results
```

## dispatch_and_wake() 函数（主 Agent 端）
```python
def dispatch_and_wake(agent_name, task_id, goal):
    import os, json, time
    pending_dir = os.path.expanduser("~/.hermes/federation/pending/")
    os.makedirs(pending_dir, exist_ok=True)

    task_payload = {
        "task_id": task_id,
        "assignee": agent_name,
        "goal": goal,
        "status": "waiting",
        "dispatched_at": time.time()
    }
    with open(os.path.join(pending_dir, f"{task_id}.json"), 'w') as f:
        json.dump(task_payload, f, ensure_ascii=False, indent=2)

    # 通过 send_message 发飞书唤醒（子 Agent 需要被@才激活）
    send_message(target=agent_name, content=f"[@{agent_name}] 联邦任务已下达：{task_id}。请立即 check_federal_pending 执行。")
```

## 闭环流程
```
dispatch_and_wake() → 写 pending/ → 发飞书 @ 唤醒
    子 Agent: 收到 @ → check pending → emit_result()
    主 Agent: scan_callbacks() → 读 done → 归档 pending 删除
```

## ⚠️ Cron Job 与 Federation Pending 断连（2026-04-27）

**现象**：子 Agent 的 cron job 完全不读 `~/.hermes/federation/pending/`，已写入的 pending 任务永远不被执行。

**根因**：
- cron job prompt 与 SOUL.md 是**两套独立配置**
- cron job prompt 写死 `从 ~/.hermes/profiles/researcher/memories/research_tasks.md 读取`
- cron job 引用的 skill `hermes:hermes-agent` **不存在**（导致技能加载退化）
- SOUL.md 里写了 V3.0-Trigger 协议，但 cron job prompt 里完全没有

**修复**：
- 用 `cronjob(action='update', job_id=..., prompt='...')` 更新 cron job prompt
- 在 prompt 最前面插入完整的 pending/ 扫描 + emit_result() 逻辑
- 不依赖 skill 引用（skill 名称可能不存在），直接在 prompt 里写死所有函数实现
- **清空 `script` 参数**（见下方坑点）

**验证要点**：更新 cron job 后，下次触发时检查：
1. `~/.hermes/federation/pending/` 下新建任务是否在下次 cron 触发时被读取
2. 任务状态是否从 `waiting` → `processing` → `done`
3. 回执是否写入 `callbacks/`
4. 检查 `~/.hermes/cron/output/{job_id}/*/latest.md` 是否有 `Script not found` 错误

## ⚠️ Cron Job `script` 参数致命误用（2026-04-27 新发现）

**现象**：`cronjob(action='update', job_id=..., script='export HERMES_HOME=...')` 设置的环境变量不生效，所有 cron run 都报错 `Script not found: export HERMES_HOME=...`。

**根因**：`script` 参数是**脚本文件路径**，不是环境变量注入。把 `export HERMES_HOME=...` 写入 script 会导致 cron 系统去找名为 `export HERMES_HOME=...` 的脚本文件。

**错误示例**：
```python
# ❌ 错误
cronjob(action='update', job_id='xxx', script='export HERMES_HOME=/root/.hermes/profiles/vps-technician')
# 导致 "Script not found: /root/.hermes/scripts/export HERMES_HOME=..." 错误
```

**正确做法**：清空 script 参数，在 prompt 内部设置环境变量，或用 `workdir` 代替。
```python
# ✅ 正确
cronjob(action='update', job_id='xxx', workdir='/root/.hermes')
# 或在 prompt 开头写：export HERMES_HOME=/root/.hermes/profiles/vps-technician
```

**教训**：`script` 参数的设计用途是预执行脚本（如数据收集脚本），不是环境变量注入。误用它会导致整个 cron job 静默失败。

## 关键坑点
- pending/ 文件写完后必须删除，否则哨兵会持续误报超时
- 原子写入：用 /tmp/uuid.json → os.rename() 到最终路径
- send_message target 用群名而非原始 ID（`研究员` 而非 `oc_ec9a`）
- 所有子 Agent 共享同一飞书 bot 身份（Hermes 总管）
- **cron job prompt 与 SOUL.md 是独立维护的**，SOUL.md 写了协议不等于 cron job 会执行
