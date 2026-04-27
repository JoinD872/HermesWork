---
name: v2ray-xray-tcp-connection-failed
description: V2RayN 显示延迟-1（TCP连接失败）时的系统性排查与修复流程
tags:
  - v2ray
  - xray
  - 网络
  - 代理
  - VPS
---

# V2RayN / Xray 连接失败排查（延迟-1）

## 触发条件
V2RayN 显示延迟 **-1**，即 TCP 连接建立失败。

## 快速排查路径

### Step 1 — 确认 VPS/Xray 服务是否在跑
```bash
ss -tlnp | grep 8081
ps aux | grep -i xray | grep -v grep
```
- **无输出** → Xray 没启动，先 `systemctl restart xray`
- **有输出但只显示 `127.0.0.1:8081`** → ❌ 问题在这里，见 Step 2
- **有输出显示 `*:8081` 或 `0.0.0.0:8081`** → 服务端正常，继续查 Step 3

### Step 2 — 修复 Xray 只监听本地的问题
Xray 默认配置 `"listen": "127.0.0.1"` 导致公网根本进不来。

编辑 `/usr/local/etc/xray/config.json`，将：
```json
"listen": "127.0.0.1"
```
改为：
```json
"listen": "0.0.0.0"
```

重启 Xray：
```bash
sudo systemctl restart xray

# 验证
ss -tlnp | grep 8081
# 应显示 *:8081 或 0.0.0.0:8081
```

### Step 3 — 检查防火墙
UFW 防火墙需要放行 8081：
```bash
sudo ufw allow 8081/tcp comment "V2Ray-Xray"
sudo ufw status | grep 8081
```

### Step 4 — 验证公网可达（从 VPS 本地测试）
```bash
timeout 5 bash -c "echo | nc -v <公网IP> 8081" 2>&1
# 期望: Connection to <公网IP> 8081 port [*/*] succeeded!
```

## 常见坑

| 现象 | 原因 |
|------|------|
| Xray 进程在跑但 V2RayN 连不上 | Xray 只监听了 `127.0.0.1`，未绑定公网 |
| `ss` 显示 `127.0.0.1:8081` | 配置文件里 `"listen": "127.0.0.1"` |
| 防火墙已开但仍连不上 | 防火墙规则加了但没 restart Xray |
| VPS 本地 curl 代理超时 | 正常，Xray 是 VLESS/VMess 专用，不认识普通 HTTPS 请求 |

## 常见端口对照（避免混淆 8080 vs 8081）
| 端口 | 服务 | 用途 |
|------|------|------|
| **8080** | nginx | VPS 内部 HTTP 反代（SearXNG 等），**不是**代理端口 |
| **8081** | Xray | VLESS 代理，对外翻墙，V2RayN 填**这个**端口 |
| 2222 | sshd | SSH |
| 8888 | SearXNG | 搜索服务 |

## V2RayN 客户端配置参数（RackNerd 洛杉矶节点）
```
地址：192.3.241.244
端口：8081（不是8080！）
协议：VLESS
传输：WebSocket
路径：/vless-tunnel
TLS：否（WebSocket 明文传输，TLS 在 Xray 内部处理）
UUID：cf4ab9c4-962c-4165-ae75-91c310d646be
```

## 当前环境参考
- 公网 IP: `192.3.241.244`
- Xray 配置: `/usr/local/etc/xray/config.json`
- Xray 协议: VLESS + WebSocket，路径 `/vless-tunnel`
- 防火墙: UFW (active)，需手动放行端口
- Xray UUID: `cf4ab9c4-962c-4165-ae75-91c310d646be`
