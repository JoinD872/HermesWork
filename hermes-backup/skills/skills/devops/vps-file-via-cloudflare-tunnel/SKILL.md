---
name: vps-file-via-cloudflare-tunnel
description: 通过 Cloudflare Tunnel 从国内访问 VPS 文件 — 绕过防火墙入站封锁，让用户拿到可下载链接
tags: [vps, cloudflare, tunnel, file-transfer, china-gfw]
version: 2026-04-25
---

# VPS 文件分享 — Cloudflare Tunnel 方案

## 问题背景

用户电脑在国内，VPS（洛杉矶）的 SSH/HTTP/SFTP 入站全部被墙。
VPS 可以主动出站连外网，方案思路：**VPS 主动连 Cloudflare → 用户通过 Cloudflare 分配的 URL 下载文件**。

---

## 核心概念：两种认证模式的区别

| | Token 模式（`--token`） | Config 模式（`--config config.yml`） |
|---|---|---|
| 认证方式 | 只需一个 `--token` 参数 | 需要 `credentials.json`（UUID+私钥） |
| Tunnel 信息 | 存 Cloudflare 仪表盘 | 存本地 `~/.cloudflared/` |
| Ingress 路由 | **必须在仪表盘配置 Public Hostname** | 可在 config.yml 配置 |
| systemd service | `cloudflared tunnel run --token xxx` | `cloudflared tunnel run --config /etc/cloudflared/config.yml` |
| **常见错误** | ❌ 在本地 config.yml 里配 ingress → **完全无效** | ✅ ingress 规则在 config.yml 里直接生效 |

> **关键教训**：Token 模式下 cloudflared **不读取本地 config.yml 的 ingress 规则**。必须在 Cloudflare Zero Trust 仪表盘里添加 Public Hostname，分配 URL。

---

## 完整操作流程

### Phase 1：VPS 端准备

```bash
# 1. 检查 cloudflared 是否已安装
which cloudflared && cloudflared --version
# → v2026.3.0（2026-04 已验证兼容）

# 2. 检查 nginx（文件服务）
sudo systemctl status nginx
sudo ss -tlnp | grep -E "80|443"
# → nginx 监听 127.0.0.1:8080（不能改，这是 agent 环境的固定端口）

# 3. 确保 nginx 能正常响应
curl localhost
# → 应返回 200

# 4. 把待下载文件放入 nginx 根目录
sudo cp /path/to/file.zip /var/www/html/
sudo chmod 644 /var/www/html/file.zip
```

### Phase 2：Cloudflare 仪表盘配置（用户操作）

1. 打开 👉 https://dash.cloudflare.com/one/
2. 进入 **Networks → Tunnels**
3. 点击 `PC-Tunnel`（或新建 Tunnel）
4. 在 **Public Hostname** 栏点击 **Add a public hostname**
5. 填写：
   - **Subdomain**：自定义，如 `vpsfiles`
   - **Domain**：选 `trycloudflare.com`（或你自己的域名）
   - **Type**：`HTTP`
   - **URL**：`localhost:8080`
6. 点击 **Save hostname**

### Phase 3：systemd service（Token 模式）

```bash
# 创建 service 文件（已有则跳过）
sudo tee /etc/systemd/system/cloudflared.service << 'EOF'
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/cloudflared tunnel run --token <替换为你的TOKEN> --no-autoupdate
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 重载并启动
sudo systemctl daemon-reload
sudo systemctl enable cloudflared
sudo systemctl restart cloudflared

# 验证
sudo systemctl status cloudflared
# → Active: active (running)，4个 connIndex 在线 = tunnel 建立成功
```

### Phase 4：验证与使用

```bash
# 查看 tunnel 状态
sudo journalctl -u cloudflared -n 20 --no-pager

# 在仪表盘 Public Hostname 确认分配的 URL
# 类似：https://vpsfiles.trycloudflare.com
```

---

## 已知约束

- **nginx 端口固定为 8080**（agent 环境配置），cloudflared ingress URL 填 `localhost:8080`
- **用户域名可选**：`trycloudflare.com` 免费但每次重启可能变；自定义域名稳定但需额外配置 DNS
- **无需 config.yml**（token 模式），Ingress 全在仪表盘
- **不要在 token 模式下同时传 `--config` 参数**，会冲突

---

## 文件传输标准流程

1. 用户把文件上传到 VPS（SCP/SFTP → VPS 可主动接收）：
   ```bash
   # 用户侧（国内电脑），VPS 主动接收
   # 注意：SSH 出站正常，用户的 SCP 能连过去
   ```
2. 文件放到 `/var/www/html/` 下
3. 通过 Cloudflare Tunnel URL 分发下载链接给用户

---

## ⚠️ 陷阱：cloudflared 可能在 Docker 容器里运行

**这是最容易踩的坑**，会导致几小时的无效排查。

### 如何判断

```bash
ps aux | grep cloudflared | grep -v grep
```

输出示例：
```
root       12291  ... cloudflared tunnel run --token eyJh...
65532      47283  ... cloudflared --no-autoupdate tunnel --no-autoupdate run --token ...
```

如果 cloudflared 进程的 **PPID 是 `containerd-shim-runc-v2`**（或类似 `docker-containerd`），说明它跑在 Docker 容器里：

```
65532     319784  319761  ... cloudflared --no-autoupdate tunnel run --token ...
#                   ↑ this is the parent
# PPID 319761 = /usr/bin/containerd-shim-runc-v2
```

### 关键区别

| | Host 上跑 | Docker 容器里跑 |
|---|---|---|
| 管理命令 | `systemctl restart cloudflared` | `docker restart cloudflared` |
| 进程状态 | `systemctl status cloudflared` | `docker ps` |
| 日志 | `journalctl -u cloudflared` | `docker logs cloudflared` |
| credentials.json 路径 | host 的 `/root/.cloudflared/` | **容器内的** `/root/.cloudflared/`（取决于挂载） |
| systemd service | 有效 | **无效**（容器由 docker daemon 管理） |

### Docker 模式下排查步骤

```bash
# 1. 确认容器 ID
docker ps | grep cloudflare

# 2. 检查容器内 credentials（与 host 不同！）
docker exec <容器ID> ls /etc/cloudflared/

# 3. 检查容器内 token 是否是最新
docker inspect <容器ID> --format '{{range .Config.Cmd}}{{.}} {{end}}'
# → 应该显示当前使用的 token

# 4. 如果 token 过期/错误：重建容器
docker stop <容器ID> && docker rm <容器ID>
docker run -d \
  --name cloudflared \
  --restart unless-stopped \
  --network host \
  cloudflare/cloudflared:latest \
  tunnel --no-autoupdate run --token "<新TOKEN>"

# 5. 如果需要让容器访问 host 的 nginx（host 网络模式下自动互通）
# 注意：nginx 如果只监听 127.0.0.1:8080，容器用 --network host 时可直接访问
```

### 通过日志确认 ingress 规则是否生效

`docker logs cloudflared` 输出中有类似：
```
INF Updated to new configuration config="{\"ingress\":[{\"hostname\":\"proxy.cloudjoind.com\", \"service\":\"http://127.0.0.1:8080\"}...
```
**version=N** 每次配置更新会递增。如果日志里没有 `Updated to new configuration`，说明 ingress 规则还没从仪表盘同步过来（刚创建时可能需要等待 30 秒）。

### Token 格式识别

```
JoinD-tunnel token：eyJhIjoiYmYyYTMxM2VjNjhhM2IwN2JmMDk0MjM4ZjQ3NWQ2YjUiLCJ0Ijoi...
PC-Tunnel token：eyJhIjoiNjc5NjQ0MjUtYmY0YS00MzVkLWFmOTgtNGU3MGMxN2E1YTRjIi...
```
前缀 `"eyJhIjoi"` 解码后是 `{"id":"..."` — 第一个字段就是 Tunnel ID。同一个 tunnel 的 token 前缀相同。

Docker 容器内的 `/root/.cloudflared/` 是容器内部的 filesystem，与 host 的 `/root/.cloudflared/` **完全隔离**。

- 如果容器用 `docker run --token` 启动 → 不需要 host 上的 credentials.json
- 如果容器用 `docker run -v /root/.cloudflared:/etc/cloudflared` 挂载了 host 的目录 → 才会用到 host 的 credentials.json

### 经验法则：先确认 cloudflared 在哪跑

1. `ps aux | grep cloudflared` 找进程
2. 查 PPID：数字 1 或 systemd → host；containerd-shim → Docker
3. 多进程共存很常见（旧的没清干净），kill 前先确认是哪个

### 旧进程残留导致 502

旧进程占着同一个 tunnel token 时，新进程会报 `Provided Tunnel token is not valid`（因为 token 只能一个进程用）。

**清理步骤**：
```bash
# 找出所有 cloudflared 进程
ps aux | grep cloudflared | grep -v grep

# 对每个进程查 PPID
ps -o pid,ppid,cmd -p <PID>

# 确认哪些在 Docker 里（PPID 是 containerd-shim）
# 确认哪些是 host 上跑的 systemd 进程（PPID=1）

# Docker 容器：docker stop <容器ID>
# host 进程：kill <PID>

# 最后只保留一个（建议 Docker 模式）
```

---

## ⚠️ 陷阱：优选IP工具改 DNS 导致 Error 1033

用户使用 Cloudflare 优选IP工具后，`proxy.cloudjoind.com` 的 DNS A 记录被指向了 Cloudflare CDN 的 Anycast IP（如 `172.67.191.241`、`104.21.84.119`），而不是 tunnel 专属的路由入口。

**症状**：curl 和浏览器均返回 `Error 1033`（origin 不可达），但 tunnel 进程本身已注册成功（4个节点全连接）。

**原因**：优选IP工具把 DNS A 记录指向 Cloudflare 公共边缘 IP，Cloudflare 按普通 CDN 路由处理，不走 tunnel 的 ingress 规则。

**解法**：去 DNS 设置里把 `proxy.cloudjoind.com` 的 A 记录改回 VPS 的公网 IP（`192.3.241.244`），Cloudflare Proxy 状态设为"关闭"（灰色云）。

---

## ⚠️ 陷阱：ingress URL 的 http:// 和 https:// 必须与 nginx 匹配

**症状**：tunnel 注册正常，ingress 规则也已加载（日志可见 version=N），但访问返回 `502 Bad Gateway`。

**排查**：

```bash
# 检查 ingress 规则内容（cloudflared 日志里会打印）
sudo journalctl -u cloudflared -n 5 --no-pager | grep "Updated to new configuration"
```

日志示例：

```json
"ingress":[{"hostname":"vpsfiles.cloudjoind.com","service":"https://localhost:8080"},...]
```

**常见错误**：ingress 里 service 写的是 `https://localhost:8080`，但 nginx 只监听 HTTP（`127.0.0.1:8080` 无 TLS）。Cloudflare 尝试与 nginx 建立 HTTPS 握手，nginx 拒绝 → 502。

**解法**：去 JoinD/Cloudflare 仪表盘，把 Public Hostname 的 URL 从 `https://localhost:8080` 改为 `http://localhost:8080`。

---

## Cloudflare Tunnel 错误码详解

| HTTP 状态码 | 含义 | 典型原因 |
|---|---|---|
| **200** | 正常 ✅ | 一切通畅 |
| **530** | Cloudflare Edge 收到请求但无法连接 origin | ingress URL 写错（http vs https 不匹配）；nginx 未运行；端口不通 |
| **1033** | 路由到 origin 失败（Cloudflare 层面） | DNS A 记录指向了 CDN IP 而非 tunnel 路由；tunnel 未注册；优选IP改DNS |
| **404** | ingress 规则未匹配该 hostname | 域名没配在 tunnel 的 Public Hostname 里 |

---

## ⚠️ 多 Tunnel 共存：PC-Tunnel / Docker-tunnel / JoinD-tunnel 完全独立

同一 VPS 上可能跑多个 cloudflared 进程，属于不同 tunnel，各自有独立的 token、ingress 规则和用途。**操作任何一个之前必须确认它的身份。**

### 快速定位

```bash
# 所有 cloudflared 进程（包含容器内的）
ps aux | grep cloudflared | grep -v grep

# Docker 容器里的 cloudflared
docker ps --filter name=cloudflared

# systemd 管理的 cloudflared（host 上跑）
systemctl status cloudflared --no-pager
```

### 确认每个进程对应的 tunnel

```bash
# systemd cloudflared 用的 token
grep ExecStart /etc/systemd/system/cloudflared.service

# Docker 容器的 token
docker inspect <容器ID> --format '{{range .Config.Cmd}}{{.}} {{end}}'
```

**重要**：同一时间每个 tunnel token 只能有一个活跃连接。新进程用同一个 token 启动会导致旧连接被踢出。如果要换 token，先停旧进程再启新的。

### 操作原则

- **Docker-tunnel**：用 `docker stop/start/restart` 管理，不要动它的进程
- **PC-Tunnel（systemd）**：用 `systemctl` 管理，不要 kill 或重建 Docker 容器
- **改任何 tunnel 的 ingress 规则**后，该 tunnel 的 cloudflared 进程会自动从仪表盘同步新规则（通常10-30秒生效）

---

## 故障排查

| 症状 | 原因 | 解决 |
|---|---|---|
| `Authentication error` | Token 过期或错误 | 仪表盘重新生成 Token |
| 访问 URL 返回 **530** | Ingress URL 配置错误（http vs https 不匹配）；nginx 未运行 | 检查仪表盘 Public Hostname 的 URL；确认 nginx 监听端口 |
| 访问 URL 返回 **1033** | DNS A 记录指向了 CDN IP 而非 tunnel 路由；优选IP工具改DNS | 检查 DNS A 记录，改为直指 VPS IP；Cloudflare Proxy 关掉 |
| 502 + credentials.json 不存在 | Docker 容器内的 token/凭证过期 | `docker exec` 检查容器内实际使用的 token，必要时重建容器 |
| 530 + cf-ray 正常返回 | Cloudflare 能收到请求但连不上 origin | 检查容器内 cloudflared 的 ingress 配置是否指向正确端口 |
| ps 显示 cloudflared 进程 PPID=1 但 service 状态 dead | systemd service 被 kill 掉但进程仍在 | 确认是否在 Docker 里跑 → 用 docker 命令管理 |
| curl localhost 失败 | nginx 未运行 | `sudo systemctl start nginx` |

## ⚠️ 陷阱：nginx `sites-enabled` 加载顺序导致 server_name 匹配被拦截

**症状**：VPS 本地 `curl https://vpsfiles.cloudjoind.com/` 返回的是"OK"（xray 的响应），而不是目录列表。cloudflared ingress 和 nginx 本身都正常。

**原因**：nginx 启动时按 **字母顺序** 加载 `sites-enabled/` 里的配置文件。如果 xray.conf 先于 vpsfiles.conf 加载，那么当请求 `Host: vpsfiles.cloudjoind.com` 到达时，nginx **先遍历 xray.conf 的 server block**（因为 xray.conf 文件名字母序更小），xray 的 server_name 写的是 `proxy.cloudjoind.com`，不匹配，但 `location = /` 是精确匹配根路径，nginx 在找到精确匹配的 location 块后就不再继续查找更合适的 server block 了，直接返回 xray 的 `return 200 "OK";`。

**解法**：把 `/vless-tunnel` 相关的 proxy 单独放在一个 server block 里（与 vpsfiles 的目录浏览配置完全分离），避免 `location = /` 误拦截。然后确保 nginx sites-enabled 加载顺序正确（也可以重命名配置文件，如 `09-xray.conf` 和 `10-vpsfiles.conf`），或直接彻底重启 nginx（`pkill nginx && nginx`）让配置重新排序。

**验证**：
```bash
# 列出 nginx 实际加载的 server block 顺序
nginx -T 2>&1 | grep -A2 "server_name"

# 本地测试（vpsfiles 应返回 HTML 目录列表，不是 OK）
curl -s --max-time 5 https://vpsfiles.cloudjoind.com/ | head -5

# proxy 的 vless-tunnel 应返回 Bad Request（xray 拒绝非 WS，正常）
curl -s --max-time 5 https://proxy.cloudjoind.com/vless-tunnel
```
| **VPS 本地 curl 正常，但公网访问 1033** | DNS 问题（A 记录指向 CDN IP 而非 tunnel） | 见"优选IP陷阱"章节 |
