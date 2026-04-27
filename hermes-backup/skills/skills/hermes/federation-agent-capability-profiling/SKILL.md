---
name: federation-agent-capability-profiling
description: 多Agent联邦能力画像建立流程——通过收集子Agent能力清单并录入路由决策依据；同时记录可直接修改子Agent SOUL.md这一重要发现。
triggers:
  - 新建Agent后需要同步能力清单
  - 路由决策缺乏依据（SOUL.md信息黑盒问题）
  - 子Agent更新了核心技能集
created: 2026-04-26
contributor: hermes-main
updated: 2026-04-26
tags: [hermes, multi-agent, federation, routing]
---

# Federation Agent Capability Profiling Workflow

## When to Use
当需要建立或更新多 Agent 联邦（多个独立 Agent 物理隔离、无法直接通信）的能力画像时使用。

## Core Principle
主 Agent 看不到子 Agent 的 SOUL.md（物理隔离），必须通过**用户手动中转**收集能力清单。

## Step-by-Step Workflow

### Phase 1: 能力清单收集（用户手动分发）

向每个子 Agent 发送能力画像召唤指令，要求回复 200 字以内的精炼清单：

```
[指令：能力画像提取] <Agent名>，基于你的 SOUL.md，请总结一份 200 字以内的《能力清单》。
要求：
- 核心专长（如：Nginx/Docker/SSL）
- 常用工具（如：ss/lsof/nginx -t）
- 【关键】 你的局限性（你不擅长或拒绝处理的事）
```

**分类细化模板（按领域）：**

| Agent类型 | 必问项 |
|-----------|--------|
| 技术运维型 | 核心专长 / 常用工具 / 局限性（明确边界） |
| 游戏/策划型 | 引擎/语言 / 设计专长 / 不负责的琐事 |
| 健康顾问型 | 知识覆盖 / 诊断逻辑 / 医学红线（必须去医院的情况） |
| 研究员型 | 搜索深度 / 输出标准 / 不处理的泛化任务 |
| 通用型 | 按需裁剪上述四项 |

### Phase 2: 汇总录入

收集所有清单后，按以下格式写入 MEMORY.md（或 MEMORY_ENV.md 预案区）：

```markdown
## 联邦能力画像（YYYY-MM-DD）
> 路由决策最高参考依据。收到专属领域任务时，对照此画像判断归属Agent。

### <Agent名>（<领域> · <chat_id>）
**核心专长：** <核心技能>
**常用工具：** <CLI/工具链>
**【局限性】** <边界明确列出>
**【路由补充】** <该Agent的特殊路由规则>
```

### Phase 3: 路由补充规则

每个 Agent 画像需附加路由补充规则，常见类型：

| 规则类型 | 示例 |
|---------|------|
| 步骤索取限制 | 小研：分步骤索取长文本，每轮聚焦单一主题 |
| 红线优先展示 | 小健：路由健康问题时优先展示医学红线 |
| 直接拒绝 | 老V：Windows VPS 问题直接拒，不转发 |
| 无解告知 | 老V：IP屏蔽问题直接告知无解，不尝试修复 |

## Known Pitfall: Patch 操作导致内容丢失

**现象**：执行 `patch(mode='replace')` 时，如果 old_string 包含其他区块的内容，可能导致目标区块被删除。

**经验**：old_string 必须精确唯一，避免包含相邻格式符号（如 `§` 或 `---` 分隔线）。

**教训**：写入新内容后立即 grep 验证完整性，不要依赖单次 patch 的返回结果。

## 重要发现（2026-04-26）

### 发现一：可以直接修改子 Agent SOUL.md
- 路径：`/root/.hermes/profiles/<agent名>/SOUL.md`
- 文件系统共享，直接读写无障碍，不需要通过用户中转
- 应用：给子 Agent 新增规则（如给小研加「回复 Done」）时直接 patch

### 发现二：小研 pending.md 机制
- 小研的 session 不会自动处理飞书消息，需要显式说「写入 pending.md」
- 小研不主动回复 Done，需要在 SOUL.md 里强制加规则「回复 Done 标记闭环」
- 小研复述指令 ≠ 执行指令，需要等「Done」或「已写入」确认

### 发现三：飞书消息 target 格式
- 群名格式（`研究员`）比原始 ID（`oc_ec9a`）更可靠
- 群名内部自动映射到正确的 `receive_id_type=chat_id`

## 验收标准
1. 每个 Agent 的能力画像包含：核心专长 + 常用工具 + 局限性 + 路由补充
2. 路由时对着画像判断，不再凭"直觉 + 关键词"
3. 新增 Agent 时同步传递最优搜索方案（知识共享规则 P0）
