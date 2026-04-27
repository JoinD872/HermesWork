---
name: minimax-coding-plan-mcp-debug
description: MiniMax Coding Plan MCP server understand_image 故障排查与请求体格式修复
tags: [mcp, minimax, debugging]
last_updated: 2026-04-25
---

# MiniMax Coding Plan MCP — 故障排查与修复知识

## 2026-04-25 关键发现

### understand_image 请求体格式（核心修复）

MiniMax `/v1/coding_plan/vlm` API **只接受** 以下格式：

```json
{
  "image_b64s": ["<纯base64字符串>"],
  "prompt": "描述文本"
}
```

**⚠️ 注意事项：**
- `image_b64s` 必须是**纯 base64**，不带 `data:image/...;base64,` 前缀
- `process_image_url()` 返回的是 `data:image/jpeg;base64,...`，需要 strip 前缀：
  ```python
  pure_b64 = processed_image_url
  if ',' in pure_b64:
      pure_b64 = pure_b64.split(',', 1)[1]
  payload = {"image_b64s": [pure_b64], "prompt": prompt}
  ```

### 错误方向（已验证不通）

以下格式 API 均返回参数错误或失败：
- ❌ `{"prompt": "...", "image_url": "data:image/..."}` — MCP 原始格式
- ❌ `{"model": "MiniMax-VL1", "messages": [...]}` — OpenAI Vision 格式，MiniMax 不支持

### Response 需要包装

API 返回：`{"content": "...", "base_resp": {"status_code": 0}}`

MCP 应包装为 OpenAI 兼容格式：
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

## 文件路径

MCP server 源码：`/root/.cache/uv/archive-v0/8tIlWQXZR8Rm9VZLOL1Jm/lib/python3.11/site-packages/minimax_mcp/server.py`

## API Key 说明

- 当前环境 key 为掩码格式 `sk-cp-...i2lo`
- curl 测试验证过该 key 配合 `image_b64s + prompt` 格式可返回 200
- MCP server 启动：`MINIMAX_API_KEY="..." MINIMAX_API_HOST="https://api.minimaxi.com" /root/.local/bin/uvx minimax-coding-plan-mcp`

## 排查原则

```
curl 成功 + MCP 失败 → 问题在请求体，不在 key
```
