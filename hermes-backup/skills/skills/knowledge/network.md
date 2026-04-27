# 网络知识库

> 小V的VPS/VPN/V2rayn知识储备，持续更新

---

## 一、VPS 基础

### 常用参数
| 项目 | 说明 |
|------|------|
| 内存 | KVM常见1G/2G/4G，OpenVZ可超售 |
| 硬盘 | SSD优先，HDD便宜但慢 |
| 带宽 | 100Mbps-10Gbps，不限流量更贵 |
| 地区 | 香港、日本、美国西海岸延迟低 |
| 架构 | amd64(x86_64)最通用，arm64省电 |

### 常用检测命令
```bash
# 配置信息
cat /etc/os-release
free -h
df -h
nproc

# 带宽测速
wget -O /dev/null http://speedtest.tokyo2.linode.com/100MB-tokyo.bin
speedtest-cli

# 延迟
ping -c 5 8.8.8.8
traceroute 8.8.8.8

# 回程路由
curl -s http://v2.iocevelasco.com/besttrace.sh | bash
```

---

## 二、网络加速方案

### BBR vs CUBIC vs BBRv2
| 算法 | 特点 | 适用场景 |
|------|------|----------|
| BBR | Google出品，吞吐高 | 高带宽高延迟链路 |
| CUBIC | Linux默认，稳定 | 普通环境 |
| BBRv2 | BBR改进，友好度更好 | 替代BBR |

```bash
# 开启BBR
echo "net.core.default_qdisc=fq" >> /etc/sysctl.conf
echo "net.ipv4.tcp_congestion_control=BBR" >> /etc/sysctl.conf
sysctl -p

# 验证
sysctl net.ipv4.tcp_congestion_control
```

### 端口加速
- **Finalspeed**：单边加速，适合带宽高延迟高
- **KCPTUN**：KCP协议，适合丢包高的链
- **UDPspeeder**：双倍发包，带宽换稳定

---

## 三、VPN协议对比

### WireGuard
- 现代协议，代码量极小（~4000行）
- 比OpenVPN/IPSec快很多
- 自动分配IP，配置极简
- 缺点：中国大陆需要额外混淆

### OpenVPN
- 成熟稳定，兼容性好
- 可走TCP 443端口伪装
- 速度比WireGuard慢

### IPSec (L2TP/IKEv2)
- IKEv2：移动设备切换网络不掉线
- L2TP/IPSec：古老但通用

### 对比速查
| 协议 | 速度 | 穿透性 | 配置难度 |
|------|------|--------|----------|
| WireGuard | 最快 | 难（UDP被封） | 简单 |
| OpenVPN | 中等 | 强（TCP伪装） | 中等 |
| IKEv2 | 快 | 中等 | 简单 |
| Shadowsocks | 快 | 强 | 简单 |

---

## 四、V2ray / Xray 核心知识

### 区别
- **Xray**：V2ray的分支，更新快，支持VLESSReality等新协议
- **V2ray**：更成熟，社区大

### 常用协议
| 协议 | 特点 | 备注 |
|------|------|------|
| VMess | 传统协议 | 需要时间同步 |
| VLESS | 无状态，更轻量 | 推荐 |
| VLESS+Reality | 目前最强抗封锁 | Xray独有 |
| Trojan | 轻量快速 | 走TLS |

### VLESS+Reality 配置要点（Xray）
```json
{
  "inbounds": [{
    "listen": "0.0.0.0",
    "port": 443,
    "protocol": "vless",
    "settings": {
      "clients": [{"id": "UUID-HERE"}],
      "decryption": "none"
    },
    "streamSettings": {
      "network": "tcp",
      "security": "reality",
      "realitySettings": {
        "dest": "www.microsoft.com:443",
        "serverNames": ["www.microsoft.com"]
      }
    }
  }]
}
```

### 伪装网站（splice/dest）常用
- `www.microsoft.com:443`
- `www.google.com:443`
- `www.amazon.com:443`
- `www.apple.com:443`

---

## 五、Xray 安装命令

```bash
# 官方推荐（Xray）
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install

# 验证
xray version

# 目录
/etc/xray/        # 配置
/usr/local/bin/xray  # 二进制

# 重启
systemctl restart xray
```

---

## 六、网络排查命令

```bash
# 端口连通性
nc -zv google.com 443
timeout 5 curl -v https://google.com

# DNS
nslookup google.com
dig google.com
cat /etc/resolv.conf

# 路由
traceroute -I 8.8.8.8
mtr 8.8.8.8

# 连接状态
netstat -tulnp
ss -tulnp

# 防火墙
ufw status
iptables -L -n
```

---

## 七、常用代理工具

| 工具 | 类型 | 特点 |
|------|------|------|
| Xray/V2ray | 平台 | 功能强，协议多 |
| Clash | 平台 | 订阅方便，GUI多 |
| Shadowrocket | iOS | 轻量移动端 |
| V2rayN | Windows/Android | 原生支持VMess/VLESS |
| Clash Verge | Windows | Clash.Meta内核 |
| sing-box | 平台 | 新锐，支持hysteria2 |

---

## 待深入学习
- [ ] hysteria2 协议部署
- [ ] Cloudflare WARP使用
- [ ] VPS防封指南
- [ ] 负载均衡方案
- [ ] Docker网络配置

---

## 八、高级网络协议

### 8.1 WireGuard 工作原理

WireGuard是基于UDP的现代VPN协议，核心概念：

```
加密隧道端点 (Peer A)                    加密隧道端点 (Peer B)
公钥 Pub-A  私钥 Priv-A                公钥 Pub-B  私钥 Priv-B
     ↓                                        ↓
  隧道IP: 10.0.0.1                     隧道IP: 10.0.0.2
     ↓                                        ↓
  公网IP: 1.2.3.4 :51820               公网IP: 5.6.7.8 :51820
```

**建立连接过程**：
1. A向B发送握手起始（handshake initiation）
2. B用自己的私钥解密验证，计算临时会话密钥
3. B响应握手响应（handshake response）
4. A验证后建立加密隧道

**特点**：
- 代码量仅~4000行（OpenVPN 100万行）
- 加密算法：Curve25519（密钥交换）+ ChaCha20（加密）+ Poly1305（认证）
- 比IPSec/OpenVPN快3-5倍
- 不存在后门风险

**WireGuard配置示例**：
```ini
# 服务端 /etc/wireguard/wg0.conf
[Interface]
PrivateKey = <服务器私钥>
Address = 10.0.0.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT
PostUp = iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

[Peer]
PublicKey = <客户端公钥>
AllowedIPs = 10.0.0.2/32

# 客户端
[Interface]
PrivateKey = <客户端私钥>
Address = 10.0.0.2/24

[Peer]
PublicKey = <服务器公钥>
Endpoint = 1.2.3.4:51820
AllowedIPs = 0.0.0.0/0  # 0.0.0.0/0 表示全局代理
PersistentKeepalive = 25  # NAT穿透保活
```

### 8.2 Cloudflare WARP+

Cloudflare WARP是用CF边缘节点做代理的服务，核心优势：
- 1.1.1.1 DNS加密
- WARP+代理（付费）
- 支持WireGuard协议

**安装使用**：
```bash
# 安装 warp-cli
apt install wireguard-tools

# Cloudflare WARP客户端
wget https://pkg.cloudflareclient.com/cloudflare-warp-latest-amd64.deb
dpkg -i cloudflare-warp-latest-amd64.deb

# 注册并连接
warp-cli register
warp-cli set-mode proxy
warp-cli connect

# 验证
curl ifconfig.me
```

### 8.3 hysteria2 协议

基于QUIC协议的高速抗封锁协议，优势：
- QUIC基于UDP，不易被深度包检测(DPI)识别
- 拥塞控制好，速度优于Trojan
- 单端口多用户支持

**安装**：
```bash
# 使用 hysteria 安装脚本
bash <(curl -fsSL https://get.hy2.sh/)

# 生成证书
openssl req -x509 -nodes -newkey ec:<(openssl ecparam -name prime256v1) \
  -keyout server.key -out server.crt -subj "/CN=example.com" -days 367

# 配置示例 /etc/hysteria/config.yaml
listen: ":443"

tls:
  cert: "/etc/hysteria/server.crt"
  key: "/etc/hysteria/server.key"

auth:
  type: password
  password: your_password_here

masquerade:
  type: proxy
  proxy:
    url: https://www.bing.com
    rewriteHost: true
```

### 8.4 Xray VLESS+Reality 进阶

VLESS+Reality是当前最强的抗封锁协议组合：
- VLESS：无状态的轻量协议
- Reality：TLS真流量模拟，目标网站选择很重要

**如何选择伪装目标（splice/dest）**：

好的目标网站特征：
1. TLS 1.3 + 不支持HTTP2（防止h2指纹泄露）
2. 证书链短
3. 证书与域名匹配
4. 长期稳定不宕机

推荐目标（2024实测）：
```
www.microsoft.com:443      # 常用，稳定
www.apple.com:443         # 苹果，证书完美
www.linkedin.com:443      # 商务网站，不易被封锁
www.ebay.com:443          # 电商平台
```

**x25519密钥对生成**：
```bash
# 生成VLESS+Reality需要的密钥
docker run teddysun/xray:latest x25519

# 输出示例：
# Private key: xxxxx
# Public key: xxxxx
# Short ID: xxxxx
```

### 8.5 负载均衡方案

**方案1：DNS负载均衡**
- 同一域名配多个A记录
- 缺点：无法健康检查，无法动态切换

**方案2：HAProxy**
```haproxy
frontend https_in
    bind *:443
    mode tcp
    default_backend web_servers

backend web_servers
    mode tcp
    balance roundrobin
    option httpchk GET /health
    server s1 10.0.0.1:443 check inter 3s fall 3 rise 2
    server s2 10.0.0.2:443 check inter 3s fall 3 rise 2
    server s3 10.0.0.3:443 check inter 3s fall 3 rise 2
```

**方案3：Nginx负载均衡**
```nginx
upstream backend {
    least_conn;  # 最少连接优先
    server 10.0.0.1:443 weight=5;
    server 10.0.0.2:443 weight=3;
    server 10.0.0.3:443 backup;  # 备用服务器
}

server {
    listen 443 ssl;
    location / {
        proxy_pass https://backend;
        proxy_set_header Host $host;
    }
}
```

**健康检查脚本（配合cron）**：
```bash
#!/bin/bash
# 检测后端存活，自动剔除/恢复
FAIL_COUNT=0
MAX_FAIL=3

for ip in 10.0.0.1 10.0.0.2 10.0.0.3; do
    if curl -sf --max-time 5 https://$ip/health > /dev/null 2>&1; then
        echo "$ip is up"
        FAIL_COUNT=0
    else
        FAIL_COUNT=$((FAIL_COUNT+1))
        if [ $FAIL_COUNT -ge $MAX_FAIL ]; then
            echo "$ip is down, removing from pool"
            # 剔除：修改nginx upstream配置，重载
        fi
    fi
done
```

---

## 九、Docker 网络配置

### 9.1 Docker网络模式

| 模式 | 说明 | 使用场景 |
|------|------|---------|
| bridge（默认） | docker0网桥，NAT上网 | 普通容器 |
| host | 共享宿主机网络栈 | 性能敏感 |
| overlay | 跨主机容器通信（Swarm） | 集群 |
| macvlan | 容器有独立MAC和IP | 需直接暴露 |
| none | 禁用网络 | 隔离环境 |

**查看Docker网络**：
```bash
docker network ls
docker network inspect bridge
```

### 9.2 自定义Bridge网络

```bash
# 创建自定义网络（支持DNS解析）
docker network create --driver bridge --subnet=172.20.0.0/16 mynet

# 启动容器加入该网络
docker run --network=mynet --name=mycontainer -d nginx

# 容器间通过名字DNS解析
docker exec mycontainer ping -c 2 othercontainer
```

### 9.3 容器端口映射

```bash
# 映射单个端口
docker run -p 8080:80 nginx

# 映射多个端口
docker run -p 80:80 -p 443:443 nginx

# 指定主机IP
docker run -p 192.168.1.100:8080:80 nginx

# udp端口
docker run -p 53:53/udp some-dns-server
```

### 9.4 macvlan模式（容器直获IP）

```bash
# 创建macvlan网络
docker network create -d macvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  -o parent=eth0 pub_net

# 容器加入macvlan（直接获得局域网IP）
docker run --network=pub_net --ip=192.168.1.50 nginx
```

### 9.5 代理容器流量（Docker + V2ray/Xray）

```bash
# 创建代理网络
docker network create proxy_net

# 启动V2ray代理容器
docker run -d --network proxy_net \
  -p 1080:1080 \
  --name=v2ray-proxy \
  v2fly/v2fly-core run -config /etc/v2ray/config.json

# 其他容器通过容器名DNS连接代理
docker run --network proxy_net \
  -e http_proxy=http://v2ray-proxy:1080 \
  python:3.10 bash

# 验证
docker exec <container_id> curl -x http://v2ray-proxy:1080 ipinfo.io
```

### 9.6 常见问题

**容器无法访问外网**：
```bash
# 检查docker0网桥
ip addr show docker0

# 检查NAT转发
iptables -t nat -L -n

# 可能是宿主机防火墙问题
systemctl stop ufw
# 或
firewall-cmd --add-masquerade --permanent
firewall-cmd --reload
```

**Docker DNS解析失败**：
```bash
# 确认resolv.conf有DNS
cat /etc/resolv.conf

# 手动指定DNS
docker run --dns=8.8.8.8 nginx

# 或在 /etc/docker/daemon.json 配置
{
  "dns": ["8.8.8.8", "1.1.1.1"]
}
```
