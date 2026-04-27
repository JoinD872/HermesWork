---
name: feishu-direct-image-sharing
description: 用户直发图片 vs 服务器本地图片的识别路径选择
---
# Feishu 直传图片识别流程

## 背景
当用户通过飞书发送图片时，图片直接加载到对话上下文中，图片识别工具（如 `vision_analyze`、`browser_vision`）可以直接访问。

**这是最可靠的方式**，应该作为优先方案。

## 正确流程

### 1. 用户直接发送图片（优先）
- 用户直接将图片拖入/粘贴到飞书对话框
- Agent 立即可用 `vision_analyze` 或 `browser_vision` 分析
- **无需下载、中转、URL访问**

### 2. 图片已在服务器本地（备选）
如果图片文件已在 VPS 本地（如 `/tmp/xxx.jpg`），但工具无法直接访问：

#### 方案A：临时 HTTP 服务器（推荐）
```bash
# 用 hermes-agent 的 venv Python 启动（避免 pip 安装冲突）
/root/.hermes/hermes-agent/venv/bin/python3 -m http.server 9002 --directory /tmp
# 然后用 browser_vision 访问 http://<公网IP>:9002/filename.jpg
```

#### 方案B：转换为 PNG 后尝试 vision_analyze
```bash
/root/.hermes/hermes-agent/venv/bin/python3 -c "
from PIL import Image
img = Image.open('/tmp/xxx.jpg')
img.save('/tmp/xxx.png', 'PNG')
"
```

## 失败模式记录

### browser_vision 访问 localhost/file:// URL 失败
- `browser_navigate(url="file:///tmp/xxx.jpg")` → 页面空白
- `browser_navigate(url="http://localhost:9002/xxx.jpg")` → 页面标题显示文件名但 `browser_vision` 返回空白
- **原因**：`browser_vision` 截图的是当前页面，但图像内容不在 DOM 可访问范围

### vision_analyze 拒绝分析
- `file://` URL 直接传给它会返回 "I can't help with that"
- 需要实际可访问的 URL 或已上传到对话上下文的图片

### tesseract OCR 对 GUI 截图无效
- GUI 软件截图（JPEG）通常不含内嵌文字
- tesseract 无输出不代表图片为空

## 已知可用的图片识别路径
1. **飞书直接发送** → `vision_analyze(image_url="file://...")` ✅
2. **VPS 临时 HTTP 服务器** → `browser_navigate("http://公网IP:端口/文件")` + `browser_vision()` ✅（需公网可访问）
3. **GitHub API 下载后本地文件** → `vision_analyze(image_url="file:///local/path.png")` ❌（拒绝 file://）

## 关键经验
- 用户自己发图片是 100% 可靠方案
- GitHub 中转图片文件（通过 API 下载到本地）= 图片文件存在但工具链不支持 file:// 访问
- 发现工具链有局限时，**优先问用户直接发图片**，而不是继续绕路
