---
name: vps-health-check
description: VPS 性能与安全完整诊断 — 详细网络安全分析（防火墙/SSH暴破/UFW拦截日志/fail2ban）+ 详细机器状态（CPU/内存/磁盘I/O/服务连接/Cloudflare Tunnel日志）
version: 2.0.0
tags: [vps, security, network, linux, monitoring]
---

# VPS 完整健康检查

## ⚠️ 报告结构规范（重要）

大佬要求的报告必须包含两大块：

### 一、网络安全（详细）
- 防火墙状态 + 规则
- SSH 暴力破解来源（失败日志）
- UFW 实时拦截记录
- fail2ban 状态
- Cloudflare Tunnel 错误日志
- 外部连接分析（目的 IP 归属）

### 二、机器使用状况（详细）
- CPU 型号 + 核心数 + 当前负载详情
- 内存使用（含 swap 详情）
- 磁盘使用 + I/O 状态
- 服务连接数
- AppArmor/SELinux 状态

---

## 完整巡检命令组

### 网络安全

```bash
# ===== 防火墙状态 =====
ufw status verbose
sudo iptables -L -n

# ===== SSH 暴力破解 =====
sudo lastb -30  # 失败登录（需要 root）
last -20        # 成功登录
# 分析攻击来源 IP 和常用用户名

# ===== fail2ban =====
sudo fail2ban-client status
sudo fail2ban-client status sshd

# ===== UFW 实时拦截日志 =====
sudo tail -100 /var/log/ufw.log | grep "UFW.*BLOCK"
# 分析来源 IP、目标端口、威胁类型

# ===== Cloudflare Tunnel 错误日志 =====
sudo journalctl -u cloudflared-docker-tunnel --since "1 hour ago" | grep -i "ERR\|error"
# 检查 nginx connection refused 等错误

# ===== 外部连接分析 =====
ss -tnp                          # 活跃连接 + 进程
# 查外部连接目的 IP 归属：
for ip in $(ss -tnp | awk 'NR>2{print $5}' | cut -d: -f1 | sort -u); do
  echo -n "$ip: "; curl -s --max-time 3 "https://ipinfo.io/$ip" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('org','?'),'|',d.get('city','?'),'|',d.get('country','?'))" 2>/dev/null || echo "解析失败"
done
```

### 机器使用状况

```bash
# ===== CPU 详情 =====
lscpu | grep -E "Model name|CPU\(s\)|Thread|Core|Socket|CPU MHz|Cache"
top -bn1 | head -5
vmstat 1 3 | tail -1

# ===== 内存详情 =====
free -h
# 看 available 而不是只看 free，available > 1GB 通常 OK

# ===== 磁盘使用 =====
df -h | grep -E "^/dev"

# ===== 磁盘 I/O =====
iostat -x 1 2 | tail -20

# ===== 服务连接数 =====
ss -tnp | grep nginx | wc -l
ss -tnp | grep xray | wc -l

# ===== AppArmor =====
apparmor_status | head -15

# ===== 路由表 =====
ip route | head -5

# ===== DNS =====
cat /etc/resolv.conf | grep nameserver
```

### 服务状态汇总

```bash
ps aux | grep -E "nginx|xray|docker|cloudflared|searxng" | grep -v grep
systemctl status nginx xray cloudflared-docker-tunnel --no-pager
docker ps
```

---

## 安全判断标准

| 检查项 | 正常 | 需关注 |
|--------|------|--------|
| SSH 暴破 | fail2ban 在 jail 中，被拦截 | 有成功登录记录不在你名下 |
| UFW 日志 | 大量 BLOCK 记录（正常扫描） | 有未拦截的可疑流量 |
| 内存 | available > 1GB | available 接近 0 |
| 磁盘 | < 85% | > 85% |
| Cloudflare Tunnel | 无 ERR 日志 | 有 connection refused |
| 外部连接 | 已知服务 IP | 未知 IP 连接内网端口 |

## 已知正常情况
- UFW 拦截大量 3389(RDP)/23(Telnet)/21(FTP)/5555 等端口扫描 → 正常，说明防火墙在工作
- Apr 25 nginx 重启导致 cloudflared tunnel 瞬时 connection refused → 正常，已恢复
- VPS 出口 IP（192.3.241.244）被知乎/部分国内网站屏蔽 → 正常现象
- YouTube transcript API 被拒 → 云服务商 IP 被 YouTube 封锁，正常
