---
name: minimax-vision-fallback
description: MiniMax 图片理解 — MCP 工具故障时的备用方案，双斜杠 URL 问题排查
---
# MiniMax 图片理解备用方案

## 使用场景

`mcp_minimax_plan_understand_image` 工具失败时（如 404 / login fail / URL 错误），使用 `mmx` CLI 命令作为备用。

## 正确用法

```bash
mmx vision describe /path/to/image.jpg
```

返回 JSON 格式：
```json
{
  "content": "图片描述文字",
  "base_resp": {"status_code": 0, "status_msg": "success"}
}
```

## MiniMax 图片理解工具已知问题

### 问题1：双斜杠 URL（404 Page Not Found）

**症状：** `404 Client Error: /v1/v1/coding_plan/vlm`

**原因：** `.env` 中 `MINIMAX_BASE_URL` 或 `MINIMAX_API_HOST` 包含 `/v1`，而 server.py 的 endpoint 本身也有 `/v1/`，拼接后出现 `//v1/v1/`。

**修复：** 
- 方案A：`.env` 中 base URL 去掉 `/v1`，改为 `https://api.minimaxi.com`
- 方案B：server.py endpoint 改为 `/coding_plan/vlm`（去掉前缀 `/v1`）
- 重启 MCP server 生效

**推荐方案A**，因为 `api.minimaxi.com` 是 MiniMax API 的标准入口。

### 问题2：Shell 密码掩码

**现象：** `cat /proc/<pid>/environ` 或 `od -c /proc/<pid>/cmdline` 中，API key 显示为 `***`。

**原因：** Linux shell 安全策略（procfs mask）自动将包含 "password"、"key"、"secret" 的环境变量/命令行参数掩码为 `***`。

**排查正确方式：**
1. 直接读文件（如 `~/.hermes/.env`）— DM 可操作
2. 不依赖 /proc 读 key，改用已知正确的 key 通过其他方式验证

### 问题3：请求体格式（2026-04-25 已排除）

**澄清：** MCP server `understand_image` 使用的是 MiniMax 原生格式 `{"prompt": "...", "image_url": "data:..."}`，不是 OpenAI vision 格式。两种格式都测试过，原生格式是正确的。

## 相关文件

- MCP server 源码：`~/.cache/uv/archive-v0/<hash>/site-packages/minimax_mcp/server.py`
- API client：`minimax_mcp/client.py`
- 图片处理：`minimax_mcp/utils.py`
- 环境配置：`/root/.hermes/.env`

## 验证命令

```bash
# 测试 VLM 是否正常（需要真实 key）
mmx vision describe /path/to/test.jpg

# 查看 MCP server 当前进程
ps aux | grep minimax

# 查看当前 base URL（在新进程启动前）
cat /root/.hermes/.env | grep MINIMAX
```
