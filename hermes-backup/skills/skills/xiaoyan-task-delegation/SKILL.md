---
name: xiaoyan-task-delegation
description: 小研（凌晨研究员）任务派发规范 — pending.md 机制、派发话术模板
version: 2026-04-26
tags: [federation, delegation, 小研]
---

# 小研任务派发规范

## 核心机制

小研有独立的 `pending.md` 队列系统，**DM 消息不会自动触发入队**。必须显式告知"写入 pending.md"。

## 标准派发流程

1. 组织任务内容（格式见下方话术模板）
2. 结尾必须加一句：**"写入 pending.md"**
3. 用 `feishu:研究员` 发送

## 话术模板

```
【联邦研究任务】

小研，<任务描述>

课题一：<标题>
<背景和研究方向>
输出：<预期交付物>

课题二：<标题>
<背景和研究方向>
输出：<预期交付物>

格式：结论先行 → 背景 → 详细分析 → 应用建议 → 参考来源
回复 Done 时附上研究摘要即可。

写入 pending.md。
```

## 优先级说明

- 低优先级任务（如"空的时候研究"）也必须说"写入 pending.md"
- 不说 = 不会排队 = 小研不会处理
- **这条规则在 MEMORY.md 小研画像中已固化**

## 验证方式

⚠️ **小研不主动回复 Done**。发送任务后：
1. 观察群里他是否有主动确认
2. 若无，不要默认已执行——需用户去群里主动 @ 小研确认
3. 小研能收到消息且 bot 通信正常，但 session 隔离导致我的回复他不一定能看到

## 实战经验（2026-04-26）

**关键发现：复述指令 ≠ 执行**
- 小研可能回复"收到"或复述你的指令，但**没有真正写入 pending.md**
- 必须看到他说「已写入」才算完成闭环
- 介入流程：发送 → 等确认 → 若无 → 用户去群里 @ 他指出 → 他补写

**联邦任务分发双轨机制**
DM 派发的任务会进入 `~/.hermes/federation/pending/<task_id>.json`，而非 `memories/pending.md`。
小研每次 session 启动应执行双轨检查：

```python
# 轨道1: memories/pending.md（手动写入的低优先级队列）
with open("memories/pending.md") as f:
    content = f.read()

# 轨道2: federation/pending/*.json（DM 分发的正式联邦任务）
import os, json
fed_dir = os.path.expanduser("~/.hermes/federation/pending/")
for fname in os.listdir(fed_dir):
    if fname.endswith(".json"):
        with open(os.path.join(fed_dir, fname)) as f:
            task = json.load(f)
        # task["status"] 判断：waiting → 执行，done → 忽略
```

**小研 session 启动标准动作（每次必执行）：**
1. 扫描 `~/.hermes/federation/pending/` 中 status=waiting 的任务
2. 扫描 `memories/pending.md` 中未完成项
3. 优先处理 federation/pending 中的任务（正式派单）
4. 执行完后执行 emit_result() 写入 callbacks/，文件名 = task_id

## 优先级说明