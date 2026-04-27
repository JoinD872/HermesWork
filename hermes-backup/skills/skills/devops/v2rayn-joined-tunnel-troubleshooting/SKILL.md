---
name: v2rayn-joined-tunnel-troubleshooting
description: V2RayN 连接失败系统性排查 — 当 JoinD Cloudflare Tunnel 域名（proxy.cloudjoind.com）无法连接时的排查流程
version: 1.0.0
author: Hermes Agent
tags: [v2ray, xray, proxy, network, joined]
---

# V2RayN + JoinD Tunnel 故障排查

## 快速诊断决策树

```
V2RayN 显示延迟-1 / 502 / 连不上
├── VPS Xray 端口通吗？（nc/vs 公网IP）
│   ├── 不通 → Xray 没监听公网 → 检查 config.json listen 字段
│   └── 通但 502 → 可能是 CDN 域名问题 → 走下面
│
├── V2RayN 用的是 CDN 域名（proxy.cloudjoind.com）还是 VPS IP？
│   ├── CDN 域名 → curl https://proxy.cloudjoind.com
│   │   ├── 502 → JoinD Tunnel 回源问题
│   │   │   ├── nginx 停了？→ systemctl restart nginx
│   │   │   ├── cloudflared 进程在跑吗？→ ps aux | grep cloudflared
│   │   │   └── tunnel token 有效吗？→ JoinD 后台检查
│   │   │
│   │   └── 200 → VPS 端正常，客户端配置问题
│   │
│   └── VPS IP 直连 → curl -x http://VPS_IP:端口
│       ├── 不通 → 防火墙/端口/监听地址问题
│       └── 通但 V2RayN 连不上 → UUID/传输/路径不匹配
```

## 核心知识点

### JoinD Tunnel 架构
- V2RayN 客户端连的不是 VPS IP，而是 **JoinD Cloudflare CDN 域名**
- CDN → Cloudflare Tunnel → VPS 本地 nginx（8080）→ Xray（8081）
- **任意环节断了都导致 502**

### 洛杉矶 VPS 端口分布（大佬环境）
| 端口 | 服务 | 监听 |
|------|------|------|
| 8080 | nginx（回源必经） | 127.0.0.1 |
| 8081 | Xray vless/ws | 0.0.0.0（修复后）|
| 2222 | sshd | 0.0.0.0 |
| 8888 | SearXNG | 0.0.0.0 |

### JoinD 两个 Tunnel 进程区分
```
Docker-tunnel（systemd）→ systemctl restart cloudflared-docker-tunnel
JoinD-tunnel（Docker）  → docker restart cloudflared-joined
```

## 排查命令清单

```bash
# 1. VPS 公网端口连通性
nc -v 192.3.241.244 8081
nc -v proxy.cloudjoind.com 443

# 2. CDN 域名健康检查
curl -s --connect-timeout 5 -I https://proxy.cloudjoind.com
# 200 = 正常，502 = 回源问题

# 3. nginx 状态（回源依赖）
systemctl status nginx
ss -tlnp | grep 8080

# 4. Xray 状态和监听
systemctl status xray
ss -tlnp | grep 8081

# 5. cloudflared 进程
ps aux | grep cloudflared | grep -v grep

# 6. nginx 日志（502 原因）
journalctl -u nginx --no-pager -n 20

# 7. cloudflared 日志（JoinD tunnel 报错）
journalctl -u cloudflared-docker-tunnel --no-pager -n 10
docker logs cloudflared-joined --tail 20
```

## 修复命令

```bash
# nginx 停了
sudo systemctl restart nginx

# Xray 没监听公网（配置文件）
sudo patch /usr/local/etc/xray/config.json \
  '"listen": "127.0.0.1"' '"listen": "0.0.0.0"'
sudo systemctl restart xray
sudo ufw allow 8081/tcp comment "V2Ray-Xray"
```

## 常见错误码

| 现象 | 原因 |
|------|------|
| 延迟 -1 | TCP 三次握手失败（端口不通/防火墙/监听地址）|
| 502 Bad Gateway | Cloudflare Tunnel 回源失败（nginx 停了/tunnel 断了）|
| 200 但实际连不上 | CDN 通了但 Xray 配置不匹配（UUID/路径等）|
| 400 Bad Request | Xray 在跑但 WebSocket 握手参数不对 |
