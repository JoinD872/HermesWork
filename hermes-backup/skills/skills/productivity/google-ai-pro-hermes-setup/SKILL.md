---
name: google-ai-pro-hermes-setup
description: Google AI Pro + Hermes Agent 配置指南（2026-04 验证）
---
# Google AI Pro + Hermes 配置指南

## 核心结论（2026-04 验证）

- Google AI Pro **每月送 $10 Google Cloud credits**（官网截图确认，逐月发放，非一次性）
- **1,000 AI Credits** 是网页端专用，Hermes 不可用
- Hermes 最稳接法：**API Key 模式**，$10 自动抵扣
- **⚠️ 勿用 OAuth 模式**（google-gemini-cli），已有大规模封号记录

## 购买后操作步骤

1. 去 https://aistudio.google.com/ 申请 API Key（免费）
2. 在 Hermes 的配置文件写入 API Key 环境变量（provider: gemini）
3. 运行 `hermes model` → 选择 Google Gemini 相关选项
4. AI Studio → Settings → Billing → Monthly Spend Cap 设为 $10（防止超额）
5. 每月 $10 GCP credits 会自动抵扣 Hermes 的 API 消费

## 消费估算

按 Gemini 3 Flash 价格（$0.50/1M in, $3/1M out）：
- $10 大约够 2000万 tokens 输入
- 正常策划/代码任务强度，一个月够用

## 风险提示

- OAuth 模式已被 Google 批量封禁账号，勿用
- API Key 模式完全合规，风险为零
