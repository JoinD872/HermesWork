---
name: feishu-api
description: 飞书开放平台 API 操作 — 发图片/消息/文件，从 app_id+app_secret 获取 token
version: 1.0.0
tags: [feishu, api, image-upload, python]
---

# 飞书开放平台 API

## 认证：tenant_access_token

**注意：`auth.json` 的 credential_pool 里没有 feishu token**，需要用 app_id + app_secret 自己拿：

```python
import urllib.request, json, os

app_id = os.getenv("FEISHU_APP_ID")          # cli_xxx
app_secret = os.getenv("FEISHU_APP_SECRET")

data = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode()
req = urllib.request.Request(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    data=data, headers={"Content-Type": "application/json"}, method="POST"
)
with urllib.request.urlopen(req, timeout=30) as resp:
    token = json.loads(resp.read())["tenant_access_token"]
```

拿到的 `token` 有效期 2 小时，每次调用 API 都带上 `Authorization: Bearer {token}`。

---

## 发图片消息（完整流程）

飞书发图片需要两步：**上传得到 image_key** → **用 image_key 发消息**。

```python
import urllib.request, json, uuid, os

def feishu_upload_image(tenant_token, image_path):
    """上传图片，返回 image_key"""
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
    
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/images",
        data=body,
        headers={
            "Authorization": f"Bearer {tenant_token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["data"]["image_key"]


def feishu_send_image(tenant_token, chat_id, image_key):
    """发送图片消息到指定 chat_id"""
    payload = json.dumps({
        "receive_id": chat_id,
        "msg_type": "image",
        "content": json.dumps({"image_key": image_key})
    }).encode()
    req = urllib.request.Request(
        f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        data=payload,
        headers={
            "Authorization": f"Bearer {tenant_token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())
```

---

## 常见错误

| code | 含义 | 解决方案 |
|------|------|---------|
| 230002 | Bot not in chat | 先把 Bot 加入群聊 |
| 232009 | Chat dissolved | 群聊已解散，用新群 ID |
| 99991661 | Missing token | tenant_access_token 为空，检查 app_id/secret |
| 400 | Bad request | 检查 multipart 格式或 payload 格式 |

---

## 环境变量

```
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_HOME_CHANNEL=oc_xxx  # DM 默认 chat_id
```
