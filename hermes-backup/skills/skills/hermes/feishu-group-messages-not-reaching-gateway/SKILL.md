---
name: feishu-group-messages-not-reaching-gateway
description: 飞书群消息收不到 gateway 的排查方法 — DM 正常但群 @机器人 无反应
category: hermes
---

# 飞书群消息不触发 gateway 排查

## 症状
- DM 消息正常到达 gateway
- 群消息（@机器人）完全不到达 gateway
- 日志只有 `Inbound dm message`，无 group 消息

## 排查路径（顺序）

### 1. 确认机器人是否在群里
- 飞书群设置 → 群机器人 → 确认应用在列表中

### 2. 确认事件订阅方式（关键）
检查飞书开放平台 → 应用 → 事件订阅：

| 订阅方式 | 说明 |
|---------|------|
| 使用长连接接收事件（WebSocket）| ✅ 当前 gateway 用此模式 |
| 将事件发送到开发者服务器 | 需要配 Webhook URL，不适用 VPS |

### 3. 确认应用权限
飞书开放平台 → 权限管理 → 应用身份权限：

| 权限名 | 用途 |
|--------|------|
| `im:message` | 读取消息 |
| `im:message.group_at_msg:readonly` | 接收群 @机器人消息 |
| `im:message:send_as_bot` | 以机器人发消息 |
| `admin:app.info:readonly` | 机器人名称解析（影响 @mention）|

添加权限后需要**重新发布应用**。

### 4. 检查日志
```bash
grep "group\|Inbound\|chat_id" /root/.hermes/logs/agent.log | grep -v "dm:"
```
如果日志里完全没有群 chat_id 的 `Inbound` 条目，说明消息根本没到 gateway，是飞书平台层的问题。

### 5. 已知问题
gateway_state.json 显示 `feishu.connected=true` 但群消息不来：
- 可能是飞书应用没有「使用长连接」权限
- 或应用需要企业管理员审批才能使用 WebSocket 模式
- 或应用版本未发布

## 关键诊断：直接用 API 确认机器人是否在群里（最可靠！）

日志和飞书后台都可能被表象误导，**用 API 查询成员列表最准确**：

```python
import urllib.request, json

# 获取 token
with open('/root/.hermes/.env') as f:
    for line in f:
        if line.startswith('FEISHU_APP_SECRET='):
            secret = line.split('=',1)[1].strip(); break

data = json.dumps({'app_id':'cli_a940bbb637f99cef','app_secret':secret}).encode()
req = urllib.request.Request(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    data=data, headers={'Content-Type':'application/json'})
token = json.loads(urllib.request.urlopen(req, timeout=10).read())['tenant_access_token']

# 查询群成员
chat_id = 'oc_6dbf15aa718c29adca8d085017930a71'  # 替换为实际群ID
req = urllib.request.Request(
    f'https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/members?member_id_type=open_id',
    headers={'Authorization': f'Bearer {token}'})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
print('member_total:', resp['data']['member_total'])
print('items:', resp['data']['items'])
```

**群信息快速查询（最可靠）：**
```python
req = urllib.request.Request(
    f'https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}',
    headers={'Authorization': f'Bearer {token}'})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
print('bot_count:', resp['data']['bot_count'])   # 0 = 机器人不在群里
print('user_count:', resp['data']['user_count']) # 用户数
print('name:', resp['data']['name'])
```
- `bot_count = 0` → **机器人不在群里**（最常见根因！）
- `bot_count >= 1` → 机器人在群里，问题在别处

## 重要：测试群消息的正确方式

❌ **用 API 发消息给群来测试** — Bot 发消息不会触发 WebSocket 事件，Gateway 收不到任何回调，日志完全没反应，这种测试方式无效。

✅ **让用户在群里 @机器人 发一条消息** — 这是唯一有效的测试方式。会触发 `Inbound group message received` 日志。

## 重启后进程冲突

重启 Hermes Gateway 时，如果旧进程未完全退出：
- 日志：`Running process detected: PID XXXX ... Hermes Gateway was already running`
- 后续可能：`Killed`（系统强行杀进程）

**正确重启步骤：**
```bash
# 1. 先查有没有旧进程
ps aux | grep hermes | grep -v grep

# 2. 有的话先杀掉
pkill -f "hermes gateway"

# 3. 再启动
hermes gateway run
```

## 验证命令
```bash
hermes gateway status  # 确认 running
cat ~/.hermes/gateway_state.json  # 确认 feishu.state=connected
grep "oc_群ID" /root/.hermes/logs/agent.log | grep -v "dm:"  # 确认群消息有进入
```
