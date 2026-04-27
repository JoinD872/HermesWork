---
name: feishu-image-upload
description: 通过 Feishu 开放平台 API 上传和发送图片（tenant_access_token + multipart upload）
---
# Feishu 图片上传与发送

通过 Feishu 开放平台 API 上传和发送图片的完整流程。

## 凭证来源

Feishu Bot 凭证从**环境变量**读取（Gateway 运行时已配置）：
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`

token 不在 `auth.json`，必须通过 API 调用获取。

## 核心流程

### Step 1: 获取 tenant_access_token

```python
import os, json, urllib.request

app_id = os.environ["FEISHU_APP_ID"]
app_secret = os.environ["FEISHU_APP_SECRET"]

token_data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=token_data,
    headers={"Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req, timeout=30) as resp:
    tenant_token = json.loads(resp.read())["tenant_access_token"]
```

### Step 2: 上传图片到 Feishu

```python
import uuid, os

image_path = "/path/to/image.png"
with open(image_path, "rb") as f:
    img_bytes = f.read()

boundary = uuid.uuid4().hex
body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="image_type"\r\n\r\n'
    f"message\r\n"
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="image"; filename="{os.path.basename(image_path)}"\r\n'
    f"Content-Type: image/png\r\n\r\n"
).encode() + img_bytes + f"\r\n--{boundary}--\r\n".encode()

req2 = urllib.request.Request(
    "https://open.feishu.cn/open-apis/im/v1/images",
    data=body,
    headers={
        "Authorization": f"Bearer {tenant_token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}"
    },
    method="POST"
)
with urllib.request.urlopen(req2, timeout=30) as resp:
    image_key = json.loads(resp.read())["data"]["image_key"]
```

### Step 3: 发送图片消息

```python
payload = json.dumps({
    "receive_id": "oc_xxxxxxxxxxxx",
    "msg_type": "image",
    "content": json.dumps({"image_key": image_key})
}).encode()

req3 = urllib.request.Request(
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
    data=payload,
    headers={
        "Authorization": f"Bearer {tenant_token}",
        "Content-Type": "application/json"
    },
    method="POST"
)
with urllib.request.urlopen(req3, timeout=30) as resp:
    result = json.loads(resp.read())
    assert result.get("code") == 0, result
```

## 常见错误码

| code | 含义 | 解决方案 |
|------|------|---------|
| 230002 | Bot/User can NOT be out of the chat | Bot 不在群里，需要先加群 |
| 232009 | Chat has already been dissolved | 群聊已解散，使用新群 ID |
| 99991661 | Missing access token | token 为空，检查 app_id/app_secret |

## `send_message` 工具的坑

`send_message(target="feishu:xxx", message="/path/to/image.png")` **不会**正确发送图片——
消息内容会变成文件路径文本。

正确方式：必须用上述 API 直接上传发送，不能依赖 `send_message` 的文件路径参数。

## Bot 加群

Bot 作为 member_type=bot 加入群聊：
```python
payload = json.dumps({
    "member_role": "member",
    "member_type": "bot"
}).encode()
# POST to https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/members
```

如果群设置了机器人权限，可能需要在飞书管理后台开放。

## 飞书群 ID

- 游戏制作组：`oc_5a883cbe523b1a93ee269bba2f8536a0`
- 健康助手群：`oc_6dbf15aa718c29adca8d085017930a71`
- 凌晨研究员：`oc_ec9adb3139cd38ac706cd7a54c4d059d`
