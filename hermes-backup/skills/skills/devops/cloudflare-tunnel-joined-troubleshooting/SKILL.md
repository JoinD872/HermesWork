---
name: cloudflare-tunnel-joined-troubleshooting
description: Cloudflare Tunnel (JoinD) 故障排查 — Error 1033/530、DNS A记录冲突、优选IP干扰、架构检查清单
tags: [cloudflare, tunnel, joind, dns, vps]
last_verified: 2026-04-25
---

# Cloudflare Tunnel (JoinD) 故障排查

## 症状
- `curl https://proxy.cloudjoind.com/` → **HTTP 530 Error 1033**
- Docker-tunnel 容器运行正常，4节点全部注册
- VPS 本地 `curl localhost:8080` 返回 200 ✅
- Cloudflare Edge 收到请求但无法路由到 origin

## 根因：优选IP工具修改了DNS A记录

用户使用"优选IP"工具后，`proxy.cloudjoind.com` 的 DNS A记录从正常路由变成了指向**具体Cloudflare PoP IP**（如 172.67.191.241 / 104.21.84.119），导致 JoinD tunnel 的路由规则失效。

### 诊断命令
```bash
# 检查DNS解析
dig +short proxy.cloudjoind.com
# 正常情况：应该解析到 JoinD tunnel 分配的入口IP（不是Cloudflare Anycast IP）
# 异常情况：解析到 104.21.x.x / 172.67.x.x（Cloudflare Anycast IP）
```

### 解决步骤
1. 登录 DNS 提供商（Cloudflare Dashboard）
2. 找到 `proxy.cloudjoind.com` 的 A记录
3. **删除** 优选IP工具设置的A记录
4. 重新设置 A记录 → **VPS真实出口IP**（如 192.3.241.244）
5. 或将 Proxy 模式改为 **DNS only**（灰色云），让 JoinD tunnel 自己处理路由
6. 等待DNS传播（约1-2分钟）
7. VPS上验证：`curl -s --max-time 10 -o /dev/null -w "%{http_code}" https://proxy.cloudjoind.com/`
   - 返回 200 = 修复成功

## 重要前提：不要破坏现有tunnel

### 当前架构（2026-04-25）
| Tunnel名称 | 类型 | 用途 | 状态 |
|-----------|------|------|------|
| **Docker-tunnel** | JoinD cloudflared容器 | v2rayN翻墙节点 + 优选IP | ✅ 正常运行 |
| **PC-Tunnel** | systemd cloudflared | 文件传输（vpsfiles.cloudjoind.com）| ❌ 未配置/已停止 |
| **JoinD-tunnel** | JoinD平台侧配置 | DNS/路由规则 | 由Docker容器使用 |

### 配置前检查清单（P0）
在修改任何 cloudflared 配置前，**必须**执行：
```bash
# 1. 查看所有运行中的cloudflared进程
ps aux | grep cloudflared | grep -v grep

# 2. 查看Docker容器状态
docker ps -a --filter name=cloudflared

# 3. 查看systemd service状态
systemctl status cloudflared --no-pager

# 4. 查看所有cloudflared配置文件
ls -la /etc/cloudflared/ /root/.cloudflared/ 2>/dev/null
```

### 教训
**不要**在不了解现有架构的情况下修改tunnel配置。之前误关Docker-tunnel就是因为没有先执行检查清单，导致用户已经正常工作的配置被破坏。

## Error 1033 vs Error 530 区别
- **Error 1033**：Cloudflare Edge → Tunnel 连接失败（DNS/路由问题）
- **Error 530**：Cloudflare Edge → Origin 服务不可达（tunnel→nginx这段断了）

两者都可能是DNS A记录问题导致。
