---
name: vps-domestic-site-access
description: VPS 访问国内网站诊断与解决方案 — 百度/知乎/bilibili/微博等
tags: [network, proxy, vps, china, domestic]
version: 2026-04-22
---

# VPS 访问国内网站 — 诊断与解决方案

## 已知问题
RackNerd 洛杉矶 HostPapa IP 被部分国内网站屏蔽，curl 有时能通（DNS 轮询到可用 IP），browser tool 始终超时。

## 当前可用能力
| 能力 | 状态 |
|------|------|
| SearXNG 搜索 | 正常 |
| Bilibili 网页 | 正常 |
| 小红书 | curl ✅ / browser ❌（反爬 JS 检测） |
| 知乎 | curl ✅ 302 / browser ❌（JS fingerprint 检测，数据中心 IP 特征） |
| 百度 | curl ✅ 200 |
| CSDN | curl ❌ 超时 000（网络层直接封禁） |
| 图片理解 | mcp_minimax_plan_understand_image |

## 关键结论（经验证，排除法）
- 不是 MTU 问题（MTU 1400 试过无效）
- curl 和 browser tool 走不同网络路径，有时 curl 通 browser 不通
- Windows 代理 WSL2 无法 reach（Connection timed out）

## 诊断二分法：网络层 vs JS 层

| 类型 | curl 结果 | browser tool 结果 | 原因 | 解法 |
|------|-----------|-------------------|------|------|
| **网络层封禁** | 超时 000 | 超时 | TCP 连接被墙 | 必须住宅代理 |
| **JS 层检测** | ✅ 200/302 | ❌ 空白/拦截 | WebGL/Canvas fingerprint + IP 黑名单 | 住宅代理，修改 fingerprint 治标不治本 |

### 验证步骤
```bash
# 1. curl 测试
curl -s -m 5 -o /dev/null -w "%{http_code}" https://目标网站

# 2. 结果判断
# 000 或 timeout → 网络层封禁
# 200/302 → JS 层检测，继续 browser tool 测试
```

### JS 层检测原理
- WebGL renderer 显示 "llvmpipe" / "Software" — 数据中心特征
- Canvas/WebRTC fingerprint 不匹配真实浏览器
- 后端 API 校验出口 IP 在数据中心黑名单
- 无鼠标轨迹、headless 特征明显

## 方案一：住宅代理服务（JS 层 / 网络层封禁均有效）

| 提供商 | 价格 | 起购量 | IP 池 | 特点 |
|--------|------|--------|-------|------|
| **Scrapeless** | **$0.40/GB** | 无 | 9000万 | 最便宜，支持 SOCKS5 |
| **DataImpulse** | $1/GB | 5GB | 500万 | 低于 $1 被点名不推荐 |
| **LunaProxy** | $1.65/GB | 100GB+ | 2亿 | 无限并发 |
| **OmegaProxy** | ~$0.8-2/GB | 未公布 | 6200万 | 无共享子网，稳定性好 |
| **国内静态住宅** | ¥9.9/IP/月 | 1个IP | 静态 | 适合长期固定 IP |

> 注：$0.40/GB 的 Scrapeless 适合偶发需求；免费代理不可靠，不建议使用。

### 集成方式
config.yaml browser section 添加：
```yaml
browser:
  proxy: "http://IP:PORT"
```

## 方案二：手机做代理（长期稳定，成本低）

适合"长久方案"——用手机 4G/5G IP 作为出口，无法被识别为数据中心 IP。

### 方案 A：Localtonet 反向 SSH 隧道（更简单）

**原理：** 手机装 Localtonet App → 建立反向 SSH 隧道 → 手机流量暴露为公网 SOCKS5 代理

- **价格：** $2/隧道/月（仅运行时计费），免费版有流量限制
- **支持：** HTTP + SOCKS5，不需要 root
- **官网：** https://localtonet.com
- **下载：** Google Play 搜 "Localtonet"
- **步骤：**
  1. 手机装 App + 网站注册
  2. 创建 Proxy Server，获得 `hostname:port`
  3. VPS browser 配置该代理地址

**限制：** 手机需联网且 App 保持运行；手机关机 = 代理失效

### 方案 B：NekoBox + 链式代理（更稳定，主流跨境方案）

**原理：** 手机装 NekoBox → 通过机场节点转发 → 最终出口 IP 是手机卡 4G/5G IP

```
VPS → 手机 NekoBox → 机场节点 → 手机住宅IP出口 → 目标网站
```

**适合场景：** 需要长期稳定的住宅 IP（如账号养号、广告验证、内容采集）

**步骤（手机端）：**
1. 手机装 [NekoBox](https://nekobox.pro/)（安卓代理客户端，开源免费）
2. 导入一个机场订阅（¥10-30/月，作为转发跳板）
3. 添加一个 SOCKS5 住宅代理（购买的服务商）
4. 配置前置代理：住宅代理走机场节点转发（链式代理）
5. 开启连接，手机成为代理出口

**详细教程：**
- 图文：https://ipweb.cc/nekobox-chain-proxy-residential-ip-configuration/
- YouTube 搜索："安卓手机 静态住宅IP NekoBox 链式代理"

**成本：**
| 项目 | 费用 |
|------|------|
| NekoBox | 免费 |
| 机场订阅 | ¥10-30/月 |
| 住宅代理 | ¥9.9/IP/月 起 |
| **合计** | **约 ¥20-40/月** |

**VPS 侧配置：** 浏览器代理地址填手机 NekoBox 暴露的 SOCKS5 端口

**优势：** 出口 IP 是手机真实 4G/5G，无法被识别为数据中心；手机不关机关机一直在线

### 方案对比

| 方案 | 成本 | 稳定性 | 难度 | 适合场景 |
|------|------|--------|------|----------|
| 商业住宅代理 | $0.40-2/GB | 高 | 低 | 偶发采集 |
| Localtonet 手机隧道 | $2/月 | 中 | 低 | 临时测试 |
| NekoBox + 机场 + 住宅代理 | ¥20-40/月 | 高 | 中 | 长期运营 |

## 验证命令
```bash
# 检查出口 IP
curl -s ifconfig.me

# 测试国内网站
curl -s --max-time 8 -o /dev/null -w "%{http_code}" https://www.baidu.com
```
