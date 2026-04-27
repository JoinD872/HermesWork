---
name: vps-joined-tunnel-troubleshooting
description: JoinD Cloudflare Tunnel 故障排查与修复 — 区分 Docker-tunnel（systemd）和 JoinD-tunnel（Docker 容器）两种不同进程
tags: [cloudflare, tunnel, vps, join.d, systemd, docker]
---

# JoinD Tunnel 故障排查

## 触发条件
JoinD 后台（https://join.ddns.net.au/dashboard）显示 tunnel 状态异常（Down/0 routes）

## 诊断流程

### Step 1：先看所有 cloudflared 进程
```bash
ps aux | grep cloudflared | grep -v grep
```
输出样例：
```
65532  328156  ... cloudflared --no-autoupdate tunnel ... (JoinD-token)
root   328511  ... cloudflared tunnel run ... (Docker-tunnel token)
```

### Step 2：对照 JoinD 后台判断是哪个 tunnel 挂了
| JoinD 后台显示 | 对应进程 | 管理命令 |
|---|---|---|
| **Docker-tunnel** Down | systemd 服务 `cloudflared-docker-tunnel.service` | `systemctl restart cloudflared-docker-tunnel` |
| **JoinD-tunnel** Down | Docker 容器 `cloudflared-joined` | `docker restart cloudflared-joined` |

### Step 3：如果进程完全没了
1. 用 `cloudflared tunnel run --token <token>` 直接起
2. 建 systemd service 自启（见下方）

### Step 4：刷新 JoinD 后台确认恢复

---

## 新建 systemd 服务（Docker-tunnel）
```bash
sudo tee /etc/systemd/system/cloudflared-docker-tunnel.service > /dev/null << 'EOF'
[Unit]
Description=Cloudflared Docker Tunnel
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/cloudflared tunnel run --token <TOKEN>
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable cloudflared-docker-tunnel
sudo systemctl start cloudflared-docker-tunnel
```

**注意**：`/usr/local/bin/cloudflared` 不是 `/usr/bin/cloudflared`，写错会导致 EXEC 203。

## 两个 tunnel 的 token（2026-04-25）
- **JoinD-tunnel**（Docker 容器）：`eyJh...MyJ9`（约280字符）
- **Docker-tunnel**（systemd）：`eyJh...MiJ9`（约300字符）
- 两个 token 不同，不能混用

## 关键教训
- `docker restart cloudflared-joined` **只会重启 Docker 容器里的 tunnel**，不会影响 systemd 服务
- 如果 Docker-tunnel Down，不能用 `docker restart` 来修
- 反过来，杀 systemd 进程也不会影响 Docker 容器
- 两者是完全独立的两套进程，只是恰好都叫 cloudflared
