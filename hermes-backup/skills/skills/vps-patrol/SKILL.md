---
name: vps-patrol
description: VPS 每日定时巡检 — 检查服务状态/资源使用/隧道连通/安全日志，发现异常立即告警
tags: [vps, patrol, cron, monitoring]
category: devops
---

# VPS 每日巡检

## 触发

- Cron 自动触发：每日某时（GMT+8）
- 也可手动触发：用户说"巡检"/"检查 VPS"/"汇报状态"

## 巡检项目（按顺序）

### 1. 服务在线检查

```bash
systemctl is-active nginx
systemctl is-active xray
systemctl is-active cloudflared-docker-tunnel
docker ps | grep cloudflared-joined
ps aux | grep -E "nginx|xray|cloudflared" | grep -v grep
```

### 2. 资源使用

```bash
# CPU 负载
uptime && top -bn1 | head -3

# 内存
free -h

# 磁盘
df -h | grep -E "^/dev"

# 硬盘已用 %
df -h / | tail -1 | awk '{print $5}'
```

### 3. fail2ban 状态

```bash
sudo fail2ban-client status sshd | head -20
sudo fail2ban-client banned count
```

### 4. Cloudflare Tunnel 健康

```bash
# 检查 tunnel 是否在跑
ps aux | grep cloudflared | grep -v grep

# 检查 journal 错误（最近 1 小时）
sudo journalctl -u cloudflared-docker-tunnel --since "1 hour ago" | grep -i "ERR\|error" | tail -10
```

### 5. 网络连通性抽查

```bash
# VPS 本身能上网吗
curl -s --max-time 5 -o /dev/null -w "%{http_code}" https://www.google.com

# proxy.cloudjoind.com 能解析吗
nslookup proxy.cloudjoind.com
```

### 6. Xray 端口监听

```bash
ss -tlnp | grep 8081
```

## 告警规则

满足以下任一条件，立即飞书通知用户（不等到 cron 结束）：

| 条件 | 严重度 |
|------|--------|
| nginx / Xray / cloudflared 任一不在跑 | 🔴 严重 |
| 磁盘使用率 > 85% | 🔴 严重 |
| 内存 available < 500MB | 🟡 注意 |
| fail2ban 当天新增封禁 > 10 IP | 🟡 注意 |
| cloudflared 日志有 ERR | 🟡 注意 |
| VPS 无法访问外网 | 🔴 严重 |

## 报告格式

走 vps-status-report skill 的模板，结论先行 + 数据完整 + 数字带单位。

## Checkpoint

巡检前写：
```json
{
  "task": "vps-patrol",
  "time": "<ISO时间>",
  "next": "send feishu report"
}
```
到 ~/.hermes/vps_checkpoint.json
