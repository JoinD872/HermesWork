---
name: hermes-workflow-iteration
description: Hermes Agent + Gemini 工作流迭代方法论——用 Gemini 作为设计协作者，通过多轮 Evaluate→Decide→Write 循环来打磨复杂规范的完整流程。适用于 workflow 规范、架构设计、多角色协同协议等需要深度迭代的场景。
tags: [hermes, workflow, iteration, gemini, design-pattern, specification]
created: 2026-04-26
---

# Hermes 工作流迭代方法论

## 核心模式

```
用户 → Gemini（设计师）
          ↓ 建议
      Hermes（架构评审）
          ↓ 评估
      用户（拍板）
          ↓ 确认
      Hermes（写入 + 闭环）
```

**今日实战案例：** V2.1 工作流规范从初版 → V2.1-Patch → V2.1-Patch-Final → V3.0-P3，共经历 6 轮迭代才封版。

---

## 三步迭代循环

### 第一步：Gemini 给出建议
- Gemini 生成完整的规范补丁（标题 + 条款 + 格式）
- 用户转发给 Hermes："Gemini 回应了，你评估一下"

### 第二步：Hermes 架构评审（必须执行）
- **架构兼容性**：这个建议在我的运行环境里能实现吗？
- **可落地性**：需要改动多少文件？其他 Agent 能配合吗？
- **优先级**：是 P1 立即做，还是 P3/P4 预研？
- **Token 成本**：收益大于额外开销吗？
- 输出格式：
  > | 建议 | 结论（采纳/微调/拒绝） |
  > | 维度 | 评价 |

### 第三步：写入 + 封版
- **写入前必读**：如果文件已被其他 sub-agent 修改过，必须先读完整文件再写入
- **全文件重写 vs patch**：内容超过 3 处分散修改 → 全文件重写
- **版本标签**：每代规范要有版本标签（V2.1 / V2.1-Patch / V3.0-P3-Active）

---

## 架构兼容性判断树

```
Gemini 建议收到
    ↓
能直接写入 MEMORY.md 吗？
    ├── ✅ 能 → 直接 patch
    └── ❌ 不能（涉及其他 Agent SOUL.md）
            ├── 降级：写入 MEMORY.md 的"分发计划"章节
            └── 说明：需要人工分发指令给对应 Agent
    ↓
需要新建数据结构吗？
    ├── ✅ 可以在现有结构上扩展（如 active_sub_agents 加字段）
    └── ❌ 需要全新数据结构 → 评估：值得吗？成本高吗？
```

---

## 常见架构限制及应对

| 限制 | 场景 | 应对方案 |
|------|------|---------|
| 无法直接修改其他 Agent SOUL.md | "让小策也执行 XXX" | 在 MEMORY.md 写"需要分发的规范"，由用户手动同步 |
| 无法实现跨 Agent 自动回调 | "老V 完成后通知我" | 用影子工单协议：checkpoint 记录 → 下次 DM 主动询问用户 |
| 无法实现实时状态感知 | "DM 里问一句系统状态" | 长期目标 V3.0，短期用 Sync-Patch 告知用户转发 |

---

## 全文件重写的触发条件

当满足以下任意一条，执行全文件 `write_file`（不是 patch）：

1. 补丁涉及 3 处或以上分散修改
2. 文件出现重复章节（同一内容两个版本）
3. 文件结构已经混乱难以 patch 定位
4. 有其他 sub-agent 同时修改过该文件（看 warning 提示）

---

## 版本标签规范

| 标签 | 含义 | 适用场景 |
|------|------|---------|
| V2.1 | 基础规范 | 首次封版的稳定版本 |
| V2.1-Patch | 小补丁 | Cache-First、DM路由等小改进 |
| V2.1-Patch-Final | 大补丁 | 影子工单协议等重大功能增加 |
| V3.0-Draft-XXX | 草案 | 尚未落地的预研方案 |
| V3.0-P3-Active | 落地版本 | 草案经评估后确认落地执行 |

---

## V2.1 规范完整结构（参考案例）

```
MEMORY.md
├── 任务规范 / 浏览器环境 / 用户期望 / 图片识别
├── 重启防护 / 飞书路由 / 知识共享 / 搜索方案
├── cron 时区
├── MiniMax 图片故障（单次坑点）
├── Agent 共性缺陷
│
├── V2.1 工作流规范
│   ├── V2.1-Patch 核心原则（4条）
│   ├── 幽灵过滤
│   ├── V2.1-Patch-Final 影子工单协议（4条，含 Sync-Patch）
│   ├── 告警 SOP
│   ├── 任务分发 Wrapper
│   ├── 幽灵结果校验
│   ├── 长内容处理
│   ├── Session Reset 闭环
│   ├── active_sub_agents 数组格式
│   └── Global Knowledge 触发规则
│
├── V2.1 版本正式封版
│
└── 联邦经验共创协议 V3.0-P3-Active（所有 Agent 通用）
    ├── 强制归档准则
    ├── 原子写入保护（Lock & Append）
    └── 经验归档模板（Strict Schema）
```

---

## 经验沉淀

### 这次迭代的 4 个关键决策

1. **承认物理隔离，不硬做跨 Agent 调度** → 影子工单协议
2. **用户作为数据链路桥接联邦** → Sync-Patch
3. **多 Agent 写入用 Lock 防止冲突** → Lock & Append 协议
4. **格式约束是经验库的质量保证** → Strict Schema

### Token 成本评估

| 场景 | 额外开销 | 收益 |
|------|---------|------|
| Cache-First（先 grep 再搜索）| ~50 tokens/次 | 节省 2500-7500 tokens（避免重复踩坑）|
| Sync-Patch（生成联邦背景同步）| ~300 tokens/次 | 节省目标 Agent 的重复排查时间 |
| 影子工单协议（拦截+追踪+闭环）| ~550 tokens/次 | 节省跨 Agent 重复沟通成本 |

---

## 触发条件

使用此 skill 当：
- 需要设计/迭代一套 workflow 规范
- Gemini 给出了一组建议需要系统评估
- 规范需要多 Agent 协同且涉及架构约束
- 需要在 MEMORY.md 或其他持久文件里写入协议类内容
