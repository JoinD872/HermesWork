---
name: hermes-multi-ai-collaboration
description: Hermes Agent 多 AI 协作模式 — 主从分工/路由分流/串行审核三种模式，以及与 ChatGPT/Gemini/Claude 协作的推荐组合
tags: [hermes, multi-agent, collaboration, chatgpt, gemini, claude]
created: 2026-04-25
---

# Hermes Agent 多 AI 协作模式

## 三种协作模式

### 模式一：主从分工（最推荐）⭐
```
用户 → Hermes（总指挥）
          ↓ delegate_task
      ChatGPT / Gemini / Claude（专业执行者）
```
- 用 `role='orchestrator'` 让 Hermes 调度子 Agent
- 子 Agent 隔离运行，通过 context 传递信息
- 适合：复杂任务分工、专业任务交给专用模型

### 模式二：路由分流（自动切模型）
```
任务 → 按规则自动路由到不同模型
```
- Hermes v0.10+ 支持 Smart Model Routing
- 需要手动配置路由规则（什么任务走什么模型）
- 适合：高频自动化，按任务类型自动分配

### 模式三：串行审核（最简单）
```
策划案 → Hermes 生成初稿
              ↓ 写入文件
        ChatGPT/Claude 读取审核
              ↓
        Hermes 修订最终版
```
- 通过共享文件传递，两个 AI 完全隔离
- 不需要额外配置
- 适合：初稿+审核的场景

## 协作伙伴选择

| 伙伴 | 协作优势 | 协作弱点 |
|------|---------|---------|
| **Claude** | 代码审核、推理质量高 | 上下文 200K |
| **Gemini 2.5 Pro** | 1M 超大上下文，适合大文档分析 | 工具调用相对脆弱 |
| **ChatGPT (Codex)** | 工具调用最稳，生态成熟 | 400K 上下文，不如 Claude 聪明 |

### 模式四：Gemini 作为设计协作者（今日新增）⭐⭐⭐

```
用户 → Gemini（设计师，给建议）
          ↓
      Hermes（架构评审 + 写入）
          ↓
      用户（拍板）
          ↓
      Hermes（执行 + 封版）
```

**适用场景：** workflow 规范、架构设计、多角色协同协议的深度迭代

**今日实战：** V2.1 工作流规范通过 6 轮 Evaluate→Decide→Write 循环，从初版迭代至 V3.0-P3-Active 封版。

**关键经验：**
- Hermes 必须做"架构兼容性评审"，不能全盘接受 Gemini 建议
- 需要区分"立即可落地"和"需要 V3.0 预研"的内容
- 写入前检查文件是否被其他 sub-agent 修改过
- 超过 3 处分散修改 → 全文件重写而非 patch
- 规范类内容要有版本标签（V2.1 → V2.1-Patch → V3.0-P3-Active）

**详见：** `hermes-workflow-iteration` skill

## UE5 技术策划推荐组合

- Gemini 处理大段设计文档、需求拆解
- Claude 把关代码质量
- Hermes 负责调度和结果整合

## 参考来源
- Hermes Agent GitHub: `agent/gemini_native_adapter.py`、`agent/codex_responses_adapter.py`
- v0.8+ Native Google GenAI provider (PR #5577)
- v0.10 Smart Model Routing + SOUL.md
- ACP Editor Integration (多 Agent 协作界面)
