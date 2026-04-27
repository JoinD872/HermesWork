---
name: github-webhook-integration
description: GitHub Webhook 深度集成知识 — 基于官方文档。解决 GitHub webhook 事件触发 agent 场景下的安全和可靠性问题。
version: 1.0.0
metadata:
  hermes:
    tags: [github, webhook, security, reliability]
---

# GitHub Webhook Integration

## 核心限制（必须遵守）

### ⏱️ 10秒响应规则
GitHub 在发送 webhook 后只等待 **10秒** 获取 2XX 响应，超时则终止连接并标记为失败。

**影响**：不能在 webhook handler 里直接做耗时操作（LLM 调用、文件 I/O、网络请求）。

**正确做法**：
1. 收到 webhook → 立即返回 2XX
2. 后台异步处理（如任务队列）

**技能中已内置的解决方案**：`--deliver-only` flag 让 webhook adapter 直接转发到目标聊天，无需 LLM 推理，响应极快。

### 🔒 验签是必须的
不用纯 IP 白名单防伪造——用 webhook secret + HMAC-SHA256 验签。

GitHub 发送 `X-Hub-Signature-256` header，值格式：`sha256=<hex>`。

## 安全实践

### 1. 订阅最少量事件
只订阅你需要的具体事件，不要全量订阅。

### 2. 验签正确方式
```
HMAC-SHA256(secret, raw_request_body) → hex → compare with X-GitHub-Signature-256
```
⚠️ 用原始 body 计算，不要 parsed JSON。

### 3. IP 白名单（可选加固）
用 `GET https://api.github.com/meta` 获取 GitHub 出口 IP 列表，定期更新。
注意：GitHub 会变更 IP，静态列表需定时刷新。

### 4. SSL 验证保持开启
GitHub 默认验证 SSL 证书，**不要关闭**。

## 事件处理规范

### 必须校验两个字段

```python
# 1. 事件类型 — X-GitHub-Event header
event_type = request.headers.get("X-GitHub-Event")  # e.g., "issues", "pull_request"

# 2. 操作类型 — payload.action 字段
action = payload.get("action")  # e.g., "opened", "closed", "created"

# 3. 唯一 ID — X-GitHub-Delivery header（用于幂等去重）
delivery_id = request.headers.get("X-GitHub-Delivery")
```

### 事件过滤示例（伪代码）
```python
if event_type == "issues" and action == "opened":
    # 处理新 issue
elif event_type == "pull_request" and action == "merged":
    # 处理 PR 合并
```

## 可靠性

### 自动重放失败投递
GitHub 支持手动重放错过的 webhook。服务端恢复后，在 GitHub Webhook Settings 页面可以触发重放。

### 幂等处理
用 `X-GitHub-Delivery` header 作为幂等键，防止重复处理：

```python
processed = redis.sismember("webhook_deliveries", delivery_id)
if processed:
    return 200  # 已经在处理过了
redis.sadd("webhook_deliveries", delivery_id)
# ... 处理逻辑
```

## 与 Hermes Webhook Skill 的关系

- `devops/webhook-subscriptions` 是通用订阅管理（创建、列表、删除）
- 本 skill 是 **GitHub 侧的集成规范**，解决"如何正确接收和处理 GitHub webhook"的问题
- 两者配合使用：先创建订阅 → 再按本文档规范处理 GitHub 事件

## 关键文档链接
- Webhook 最佳实践：https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks
- Meta API（获取IP）：https://docs.github.com/en/rest/meta/meta#get-github-meta-information
- 事件类型参考：https://docs.github.com/en/webhooks/webhook-events-and-payloads
