---
name: cloudflare-joined-tunnel-architecture
description: Cloudflare JoinD托管Tunnel与标准cloudflared的关键架构差异——ingress规则优先级、Docker host网络、Error 1033排查
---

# Cloudflare JoinD Tunnel 架构关键知识

## JoinD Token vs 标准 Cloudflared Token 的本质区别

### 标准 Cloudflare Token
```
cloudflared tunnel run --token "eyJh..." 
→ 读本地 /etc/cloudflared/config.yml 的 ingress 规则
```

### JoinD Tunnel Token（托管型）
```
cloudflared tunnel run --token "eyJh...MyJ9"
→ JoinD 仪表盘的 ingress 规则通过 config 字段下发给容器
→ 本地 /etc/cloudflared/config.yml 被覆盖/忽略
```

**证据**：`Updated to new configuration config="{\"ingress\":[...]}"` 日志证明 JoinD 仪表盘在持续推送配置。

---

## 宿主机 vs Docker 容器网络

### Docker --network host 模式（正确）
```
容器内 127.0.0.1:8080 = 宿主机 localhost:8080
```
- nginx 监听 `127.0.0.1:8080` ✅
- 容器内 `curl http://127.0.0.1:8080` → 连到宿主机 nginx ✅

### Docker 默认 bridge 模式（错误）
```
容器内 127.0.0.1:8080 = 容器自己的 localhost
宿主机 nginx 在 172.17.0.1 或 eth0 IP
```
- `host.docker.internal` 在某些 Docker 版本不可用
- `172.17.0.1` ping 通但 TCP 连接被 ufw/Docker 规则拦截

---

## Error 1033 排查流程

1. **看容器日志** `docker logs cloudflared-joined`
2. **找 `Updated to new configuration`** — 确认 ingress 规则内容
3. **关键判断**：如果 ingress 里 `proxy.cloudjoind.com → http://127.0.0.1:8080` 且用 `--network host`，则 origin 连不上问题在：
   - JoinD 仪表盘的 service URL 设置（最常见）
   - 而不是本地 config.yml

---

## 实际操作原则

1. **不要改 /etc/cloudflared/config.yml**（对 JoinD token 无效）
2. **让用户去 JoinD 仪表盘改 Public Hostname 的 service URL**
3. **Docker 必须用 `--network host`**（不能用 bridge）
4. **nginx 监听 127.0.0.1:8080**（host 模式下这样更安全）

---

## 图片理解 VLM 故障

- `mcp_minimax_plan_understand_image` 在 2026-04-25 返回 "login fail" 错误（Trace: `063b8bd9ac60e5c6ee38739a6af6a371`）
- `vision_analyze` 已禁用（`auxiliary.vision.provider: ''`）
- **临时方案**：让用户口述截图里的文字，不要依赖图片理解
