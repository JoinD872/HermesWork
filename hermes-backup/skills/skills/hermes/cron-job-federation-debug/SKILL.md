---
name: cron-job-federation-debug
description: Hermes Cron Job 联邦任务调试 — 诊断 cron run 不执行、pending 不读取、callback 不写入的问题
tags: [cron, federation, debug, pending, callback]
category: hermes
---

# Cron Job 联邦任务调试手册

## 核心验证逻辑

**判断 cron job 是否真正执行了 federation 任务**：

```python
# ✅ 正确方式：检查 callback 文件 + pending 状态
import os
callback_dir = os.path.expanduser("~/.hermes/federation/callbacks/")
pending_dir = os.path.expanduser("~/.hermes/federation/pending/")

task_id = "AUTO_TEST_03"
callback_path = os.path.join(callback_dir, f"{task_id}.json")
pending_path = os.path.join(pending_dir, f"{task_id}.json")

# 1. callback 存在 = 任务执行了
# 2. pending 状态 = done = 完整闭环
print("✅ 成功" if os.path.exists(callback_path) else "❌ 未执行")
```

**❌ 不可靠的验证方式**：
- 仅检查 `~/.hermes/cron/output/<job_id>/` 是否有新 `.md` 文件
- `cronjob(action='run')` 返回 `success: true` 不保证生成了新输出文件

**✅ 可靠验证**：
- 检查 `~/.hermes/federation/callbacks/{task_id}.json` 是否生成
- callback 存在且 `status: "done"` = 任务完整执行并闭环
- 输出文件可能延迟或不生成，但 callback 不会骗人

---

## 常见坑点

### 坑1：`script` 参数误用环境变量设置

**错误写法**：
```python
cronjob(action='create', script="export HERMES_HOME=/root/.hermes/profiles/vps-technician", ...)
```

**现象**：cron 运行日志出现 `Script not found: /root/.hermes/scripts/export HERMES_HOME=...`

**原因**：`script` 参数是**脚本文件路径**，不是 shell 环境变量设置命令。系统把整个字符串当作要执行的脚本路径去调用。

**正确写法**：
- **不要**在 `script` 参数里设置环境变量
- 用 `workdir` 参数指定工作目录（`workdir: /root/.hermes`）
- 或在 prompt 内部设置：`export HERMES_HOME=... && do_something`

---

### 坑2：`.tick.lock` 阻止连续触发

**现象**：`cronjob(action='run')` 返回成功，但没有任何新输出文件

**原因**：
```
~/.hermes/cron/.tick.lock  # 存在，阻止并发
```

cron run 完成后，lock 文件**不会立即删除**（持续几分钟），后续手动 `run` 会被 lock 机制拦截。

**排查**：
```bash
ls -la ~/.hermes/cron/.tick.lock  # 存在 = 被锁
rm -f ~/.hermes/cron/.tick.lock   # 删除后重试
```

**注意**：定时触发的 cron job 本身不受影响（gateway ticker 控制），只有手动连续 `run` 才会触发此问题。

---

### 坑3：Cron Job Prompt 与 Federation Pending 断连

**现象**：pending 文件写入成功，但任务永远不被执行，callback 始终不存在

**原因**：Cron Job 的 prompt 写死了从其他文件读取（如 `research_tasks.md`），根本不扫描 `~/.hermes/federation/pending/` 目录

**排查步骤**：
1. 读取 cron job 的 prompt：`cat ~/.hermes/cron/jobs.json` 查找对应 job 的 `prompt` 字段
2. 确认 prompt 第一行是否有 pending 扫描逻辑
3. 确认 prompt 中引用的 `skills` 是否真实存在（不存在的 skill 会被跳过，但不会报错）

**修复**：在 cron job prompt 最前面插入 pending 扫描逻辑：
```
## 联邦任务接收协议（最高优先级）
每次唤醒必须先执行以下逻辑，再处理其他任务：
1. 扫描 `~/.hermes/federation/pending/` 目录
2. 若发现分配给自己的任务（`"assignee": "老V"` 且 `"status": "waiting"`），立即：
   - 将状态改为 `"processing"`
   - 执行任务内容
   - 调用 `emit_result()` 写入 `~/.hermes/federation/callbacks/{task_id}.json`
3. 若 pending/ 为空，继续执行常规任务
```

---

### 坑4：非实时 Agent 的 Webhook 通知无效

**现象**：通过飞书 Webhook 发消息给子 Agent（如小研），Agent 永远不会自动唤醒

**原因**：Webhook 消息只是普通飞书消息，不会唤醒 Agent session

**解决方案**：联邦任务不依赖飞书通知，而是：
1. 写入 `~/.hermes/federation/pending/{task_id}.json`
2. 子 Agent 的 cron job 触发时自动扫描 pending 目录
3. 主 Agent 通过扫描 `~/.hermes/federation/callbacks/` 验证闭环

---

## 调试流程图

```
cronjob(action='run') 返回后...
    │
    ├── 检查 ~/.hermes/cron/.tick.lock 是否存在
    │       └── 存在 → 删除 lock → 重新 run
    │
    ├── 检查 callback 文件是否生成
    │       └── 存在 → ✅ 任务执行成功
    │       └── 不存在 → 检查 prompt 是否接入 pending 机制
    │
    └── 检查 pending 状态是否变为 done
            └── 未变 → prompt 问题，执行修复
```

---

## Cron Job 内部机制速查

| 文件/目录 | 用途 |
|-----------|------|
| `~/.hermes/cron/jobs.json` | 所有 cron job 配置（含 prompt） |
| `~/.hermes/cron/output/<job_id>/` | 每次运行的输出 `.md` 文件 |
| `~/.hermes/cron/.tick.lock` | 防止并发的 lock 文件 |
| `~/.hermes/federation/pending/` | 联邦待执行任务 |
| `~/.hermes/federation/callbacks/` | 联邦任务回执池 |

---

*整理自 2026-04-27 凌晨调试 session，贡献者：Hermes总管*
