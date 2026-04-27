---
name: vps-status-report
description: VPS 状态报告规范 — 格式化输出网络/机器状态，包含结论先行、数据完整、所有数字带单位
tags: [vps, status, report, devops]
category: devops
---

# VPS 状态报告格式规范

## 触发条件
用户要求"报告 VPS 状态"或"汇报网络和机器状况"时触发。报告时间固定写在顶部。

## 报告原则

- **先给结论，再给数据**：一句话说明正常/有问题/有风险
- **数据要完整**：总量 / 已使用 / 剩余，三项同时列出
- **所有数字必须带单位**
- **写明数据来源**：如"来自 /proc/meminfo"、"来自 ps aux"

## 报告模板

### 一、网络安全

#### 1. 防火墙（UFW）
```
Status: active / inactive
默认策略: deny incoming / allow outgoing
放行端口: 端口 → 用途
```

#### 2. SSH 暴力破解防御
```
fail2ban sshd jail 状态: active/inactive
当前失败次数 / 历史总失败次数
当前封禁 IP 数 / 历史总封禁数
当前被封 IP 列表
攻击来源 Top N: IP / 失败次数 / 归属
```

#### 3. UFW 实时拦截
```
统计被拦截的端口和来源（最近 N 条）
威胁类型判断（RDP暴破/随机端口扫描/漏洞扫描等）
```

#### 4. 网络接口
```
接口 / 状态 / IP / MTU
```

#### 5. 端口监听
```
端口 / 服务 / 绑定地址 / 状态
```

#### 6. 当前 ESTAB 连接
```
来源 → 目标，进程，关联服务（如 V2RayN 客户端 / GCP API）
```

#### 7. Cloudflare Tunnel
```
各 tunnel 进程状态 / 运行时长 / 内存占用
已知历史错误（时间 / 错误类型 / 是否已恢复）
```

### 二、机器使用状况

#### CPU
```
型号 / 核心数 / 超线程数
当前负载（1/5/15分钟）
实时占用（user% / system% / idle%）
```

#### 内存（总量 / 已使用 / 剩余）
```
物理内存总量: X GiB
实际已使用:   X GiB（含 buffers/cache）
实际剩余:     X GiB（MemAvailable）

详细分类（/proc/meminfo）:
  字段 | kB | 约等于 | 说明

进程占用 Top N（按 RSS）:
  排名 / 用户 / PID / RSS / %MEM / 进程名 / 用途
```

#### 磁盘
```
总量 / 已用 / 可用 / 使用率

磁盘 I/O:
  读 req/s / 写 req/s / 利用率 / 状态
```

### 三、服务配置确认

| 服务 | 配置项 |
|------|--------|
| Xray | 协议 / 端口 / 监听地址 / 路径 / UUID |
| nginx | 监听地址 / server_name / 反代目标 |
| Cloudflare Tunnel | 进程数 / 各进程 PID / 运行时长 |

### 四、综合结论

表格形式：
```
检查项 | 状态 | 详情/备注
```

## 常见坑

### 内存数字换算
- `free -h` 的 used 包含 cache，不等于实际占用
- 进程 RSS 是实际物理内存，可直接加总
- `available` = 可分配给新程序的内存（含可回收 cache）

### SSH 暴力破解
海外 VPS 经常被扫描，用户名通常是 root/admin/ubuntu/debian，来自 DigitalOcean/linode 等云服务商。fail2ban 正常运行 = 防御有效。

### Cloudflare Tunnel 502
常见原因：nginx 重启导致 tunnel 回源失败，nginx 恢复后自动重连。
