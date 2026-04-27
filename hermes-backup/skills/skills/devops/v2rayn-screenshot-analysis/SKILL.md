---
name: v2rayn-screenshot-analysis
description: V2RayN 配置截图 OCR 识别 + 故障排查流程，提取节点配置参数（地址/端口/UUID/传输/路径/TLS）并判断连通性
tags: [v2ray, vpn, screenshot, ocr, network]
author: Hermes Agent
license: MIT
---

# V2RayN 截图分析与故障排查

## 截图识别流程

当用户发来 V2RayN 配置截图时：

### Step 1：识别图片格式
```bash
file <image_path>
```
图片可能是 WebP 格式伪装成 .jpg（文件头显示 `RIFF ... Web/P image`）。

### Step 2：格式转换（如需）
```python
from PIL import Image
img = Image.open('/path/to/image.jpg')
img.save('/tmp/v2ray_screenshot.png', 'PNG')
```

### Step 3：OCR 提取文字
```bash
tesseract /tmp/v2ray_screenshot.png stdout -l eng+chi
```
重点提取字段：地址、端口、UUID、传输（network）、路径（path）、TLS、SNI、fingerprint。

### Step 4：判断连接目标类型

| 目标格式 | 类型 | 说明 |
|----------|------|------|
| `192.3.x.x:443` 样式 | VPS 公网 IP 直连 | 防火墙/端口/服务状态检查 |
| `proxy.cloudjoind.com:443` | JoinD Cloudflare CDN | 检查 tunnel 链：nginx:8080 → cloudflared → CDN 域名 |
| `xxx.freedist.cloud:xxx` | 各类白嫖 CDN | 按实际域名分析 |

---

## JoinD Tunnel 502 快速诊断

```bash
# 1. 检查 CDN 域名是否通
curl -s --connect-timeout 5 -I https://proxy.cloudjoind.com

# 2. 检查 nginx 是否在跑
systemctl status nginx --no-pager | grep "Active\|Main PID"

# 3. 检查 tunnel 进程
systemctl status cloudflared-docker-tunnel.service --no-pager | tail -10
docker ps cloudflared-joined

# 4. 查看 tunnel 实时错误日志（最近 50 行）
journalctl -u cloudflared-docker-tunnel -n 50 --no-pager
```

### JoinD 依赖链（关键）
```
用户请求 → Cloudflare CDN (proxy.cloudjoind.com)
         → cloudflared tunnel (VPS 公网)
         → nginx :8080 (本地反代)  ← 关键依赖
         → Xray :8081 (VLESS 服务)
```

### 常见 502 根因

| 根因 | 日志关键字 | 修复 |
|------|-----------|------|
| nginx 停止 | `dial tcp [::1]:8080: connect: connection refused` | `sudo systemctl restart nginx` |
| Xray 停止 | `connection refused` on port 8081 | `sudo systemctl restart xray` |
| cloudflared 停止 | tunnel process not found | JoinD 后台查看状态 |
| Xray 只监听 127.0.0.1 | `nc VPS_IP 8081` 失败 | 修改 config.json: `"listen": "0.0.0.0"` |

---

## VPS Xray 配置路径
```
配置文件：/usr/local/etc/xray/config.json
服务名：xray
重启：sudo systemctl restart xray
检查：ss -tlnp | grep 8081
```
