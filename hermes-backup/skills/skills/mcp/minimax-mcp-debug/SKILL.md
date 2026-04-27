---
name: minimax-mcp-debug
description: MiniMax Coding Plan MCP server 故障排查与修复 — understand_image 工具 login fail / 请求体格式错误 / base64 前缀问题
category: mcp
---

# MiniMax Coding Plan MCP — 调试与修复知识

## 故障现象
`mcp_minimax_plan_understand_image` 工具返回 `login fail`

## 组件位置
- MCP server 源码：`/root/.cache/uv/archive-v0/<hash>/lib/python3.11/site-packages/minimax_mcp/server.py`
- API client：`/root/.cache/uv/archive-v0/<hash>/lib/python3.11/site-packages/minimax_mcp/client.py`
- 图片处理：`/root/.cache/uv/archive-v0/<hash>/lib/python3.11/site-packages/minimax_mcp/utils.py`

## 核心修复项（必须全部检查）

### 1. 请求体格式（最常出错的地方）

MiniMax VLM API **只接受**这种格式：
```json
{
  "image_b64s": ["<纯base64字符串（不带data:image/...前缀）>"],
  "prompt": "描述文本"
}
```

**常见错误格式（不要用）：**
```json
// ❌ 错误1: image_url 格式
{"prompt": "...", "image_url": "data:image/jpeg;base64,..."}

// ❌ 错误2: OpenAI messages 格式
{"model": "MiniMax-VL1", "messages": [{"role": "user", "content": [...]}]}
```

### 2. Base64 前缀必须 strip

`process_image_url()` 返回 `data:image/jpeg;base64,<data>`，需要手动去掉前缀：
```python
pure_b64 = processed_image_url
if ',' in pure_b64:
    pure_b64 = pure_b64.split(',', 1)[1]
payload = {"image_b64s": [pure_b64], "prompt": prompt}
```

### 3. Response 需要 choices 包装

MCP server 原代码直接返回 `content`，Hermes 期望 OpenAI-compatible 格式：
```python
return TextContent(
    type="text",
    text=json.dumps({
        "choices": [{
            "message": {"role": "assistant", "content": content}
        }]
    })
)
```

### 4. Client header 注意

`client.py` 中的 session headers：
```python
self.session.headers.update({
    'Authorization': f'Bearer {api_key}',
    'MM-API-Source': 'Minimax-MCP'   # 这个header存在，不影响但非必须
})
```

## 调试方法

### DEBUG 打印请求完整细节

在 `client.py` 的 `_make_request` 方法里加：

```python
import sys
print(f"[DEBUG] URL: {url}", file=sys.stderr)
print(f"[DEBUG] Headers: {dict(self.session.headers)}", file=sys.stderr)
body = kwargs.get('json')
if body:
    body_repr = body.copy()
    if 'image_b64s' in body_repr:
        body_repr = body_repr.copy()
        body_repr['image_b64s'] = [b[:40]+"...(truncated)" for b in body_repr['image_b64s']]
    print(f"[DEBUG] Body: {json.dumps(body_repr, ensure_ascii=False)}", file=sys.stderr)
print(f"[DEBUG] Response status: {response.status_code}", file=sys.stderr)
print(f"[DEBUG] Response body: {response.text[:2000]}", file=sys.stderr)
```

重启 MCP 后，通过 `process(action='log')` 查看 stderr 输出。

### 对比验证（最可靠方法）

用 Python 模拟 MCP 的实际 HTTP 请求，对比和成功 curl 的差异：
```python
import requests, json, base64

with open('test.jpg', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

payload = {"image_b64s": [img_b64], "prompt": "描述"}

session = requests.Session()
session.headers.update({
    'Authorization': 'Bearer sk-cp-...i2lo',
    'Content-Type': 'application/json'
})
resp = session.post('https://api.minimaxi.com/v1/coding_plan/vlm', json=payload)
print(resp.status_code, resp.text[:500])
```

## 关键发现（2026-04-25 验证）

**VLM 和 search 接口的 base URL 是 `https://api.minimaxi.com`（无 `/anthropic` 后缀）。**

```bash
# ✅ 正确（返回 200 或业务错误如 login fail）
curl -X POST https://api.minimaxi.com/v1/coding_plan/vlm ...

# ❌ 错误（返回 404 — nginx 不路由此路径）
curl -X POST https://api.minimaxi.com/anthropic/v1/coding_plan/vlm ...
```

**因此 `MINIMAX_API_HOST` 环境变量的值不应含 `/anthropic` 后缀。**

`.env` 中的 `MINIMAX_BASE_URL=https://api.minimaxi.com/anthropic` 是**错误的**（但 key 本身是好的）。

## 已知限制

- API key 在 Hermes 中被加密/掩码为 `sk-cp-...i2lo`，当前 session 无法获取明文
- 如果 `image_b64s + prompt` 格式仍然返回 login fail，说明 key 本身无效（与格式无关，需换 key）
- 真实 key 的配置属于 Hermes credential pool 管理范畴

## 重启 MCP server 流程

1. 杀进程：`kill $(pgrep -f "minimax-coding-plan-mcp")`
2. 拉起：`MINIMAX_API_KEY="..." MINIMAX_API_HOST="https://api.minimaxi.com" /root/.local/bin/uvx minimax-coding-plan-mcp`
3. 验证：`ps aux | grep minimax-coding-plan | grep -v grep`

注意：`uvx` 在 subprocess 环境下会缺 `realpath`/`dirname`，DEBUG 时 MCP server 必须作为 background=true 进程启动。
