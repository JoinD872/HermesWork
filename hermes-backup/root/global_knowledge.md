# Global Knowledge — 跨任务经验沉淀

> 主 Agent 上下文是宝贵资源，每一次塞入的记忆都必须是经过提纯的高价值情报。
> 本文件记录"踩过的坑"和"已验证的解决方案"，按主题分类，供每次任务开始前快速扫一眼。

---

## 飞书消息发送

### ⚠️ send_message 必须加 `feishu:` 前缀
- **错误**：`send_message(..., target="oc_xxx")` → `Unknown platform: oc_xxx`
- **正确**：`send_message(..., target="feishu:oc_xxx")`
- **何时踩坑**：cron 任务和 sub-agent 里容易忘记
- **经验**：飞书 chat_id 全部以 `oc_` 开头，发送前必须手动加 `feishu:` 前缀

### ⚠️ Cron 自动投递与 send_message 重复
- cron job 的 final response 会自动投递到 `deliver` 目标
- 不要对同一目标既用 send_message 又依赖 auto-delivery，会重复
- **经验**：DM 目标（`oc_8391fa2b38acbd759ff75ab3616d5d1f`）通常走 auto-delivery，不需要额外 send_message

---

## 图片理解

### ✅ 统一走 MMX CLI，不走 MCP
- `vision_analyze` 已禁用（MCP auxiliary.vision.provider 全为空）
- **正确方式**：`mmx vision describe <图片路径>`
- **已知 bug**：MiniMax MCP `understand_image` 有平台级 1004 login fail，不要用
- **验证**：`mmx auth status` 查认证状态，`mmx quota show` 查配额

---

## 搜索

### ✅ 搜索入口优先级（已验证最优）
1. **SearXNG** (`localhost:8888`) — 集大成，搜索质量最高
2. **mcp_searxng_search** — MCP 工具方式
3. **mcp_minimax_plan_web_search** — 备用
4. **Browser 搜索** — 以上全部失败时用

### ✅ 碰见难点必须拓展搜索渠道
- 死磕一条路不变通是 Agent 共性缺陷
- 遇到报错/卡点：官方文档 → GitHub Issues → Reddit → Discord → 社区论坛
- **不能只靠一个搜索入口**，要换关键词、换引擎

---

## VPS

### 架构关键点
- VPS 公网 IP：`192.3.241.244`（洛杉矶 RackNerd/HostPapa）
- V2RayN 客户端连 **JoinD Cloudflare Tunnel 域名** `proxy.cloudjoined.com:443`（不是直连 IP）
- CDN tunnel 回源依赖本地 nginx（`127.0.0.1:8080`），nginx 停了全 tunnel 502

### 服务端口
| 端口 | 服务 |
|------|------|
| 8080 | nginx |
| 8081 | Xray (vless/ws) |
| 2222 | sshd |
| 8888 | SearXNG (Docker) |

### VPS 出口 IP 被墙
- 百度/知乎屏蔽，bilibili ✅ 可访问
- **解决方案**：JoinD Cloudflare Tunnel 绕过国际出口封锁

---

## 浏览器环境

- agent-browser v0.26.0 + Chrome 147 + playwright v1.58.0 + camoufox 0.4.11（Firefox 内核）
- camoufox headless 已装，在 WSL/CLI 环境下可用
- 遇到"curl 能访问但浏览器无法访问"：用 `browser_network_debug` skill 排查

---

## 多 Agent 协作

### delegate_task 何时用
- ✅ **用**：推理密集型任务、多独立工作流（Research A + B 并行）、需专业子 Agent 的任务
- ❌ **不用**：简单机械操作、单步查询、需人工干预的交互任务

### 上下文传递规范（已验证）
- 将任务目标 + 约束 + 输出格式要求 **全量** 传入 `context` 字段
- leaf 子 Agent **不能再委派**（默认 role='leaf'）
- 结果聚合由主控 Agent 负责最终综合

### 跨 Agent 记忆共享
- Mesh Memory Protocol (MMP)：arXiv:2604.19540（2026.04.21），最新方案
- Hermes Agent 尚未实现真正多 Agent 记忆共享（GitHub issue #344）
- **当前可行方案**：主动用 `send_message` 推送摘要到目标群

---

## 任务持久化

### checkpoint 规范（已固化）
- 多步骤任务：每步完成后**立即**写入，不等 reset
- **双写**：`~/.hermes/task_checkpoint.json` + `memory` 工具
- 重启 Gateway 前必须写 checkpoint（任务状态 + 下一步 + 改动文件）
- 重启后必须发飞书通知

### 重启 Gateway 防护 SOP（P0）
1. 写 checkpoint（任务状态 + 改动文件 + 下一步）
2. 确认用户明确同意（禁止擅自重启）
3. 执行重启
4. 重启后飞书通知用户

---

## Session Reset

### 重置后必须立即做的事
1. 读取 `~/.hermes/task_checkpoint.json` 确认任务状态
2. 发送飞书通知告知用户已重连
3. 如有 pending 任务，从 checkpoint 恢复

---

## Cron 任务

### 时区设置
- 设置 cron 必须用**用户当地时间**（GMT+8）
- 换算：凌晨 3 点触发 = `cron` 设 `19:00 UTC`（不是 03:00 UTC）

### 执行超时
- 建议 5 分钟作为单个任务执行上限
- 超时后标记失败状态，写入 checkpoint，等待用户介入

---

---

## MMX CLI 图片生成故障（2026-04-26）

### 结论
- **API Key 绑定 cn region**（global region 返回 code 1: invalid api key）
- **cn region 图片 API 不可用**：POST `https://api.minimaxi.com/v1/image_generation` 返回 `code: 6, Network request failed`
- 文本/对话 API 正常（走同域名同 key）
- `image.minimaxi.com` 独立图片域名全局 DNS NXDOMAIN（但这不是 MMX CLI 走的端点）

### 根因
MiniMax cn 节点图片生成服务端故障，非网络/代理/域名问题

### 默认绘图工具
**切换至 pollinations.ai**（免费，VPS 可访问，格式 `https://image.pollinations.ai/prompt/<prompt>.png`）

### 验证命令
```bash
mmx config show  # 确认 region=cn, base_url=https://api.minimaxi.com
curl "https://image.pollinations.ai/prompt/a%20test.png"  # 验证替代方案可用
```

---

---

## [联邦架构] Cron Job 与 Federation Pending 断连
- 现象：小研 cron job（job_id: ef20c63571f7）完全不读 `~/.hermes/federation/pending/`，已写入的 pending 任务永远不被执行
- 根因：cron job prompt 写死 `从 research_tasks.md 读取`，与 SOUL.md 中的 V3.0-Trigger 协议脱节；引用的 skill `hermes:hermes-agent` 不存在
- 解法：更新 cron job prompt，在最前面插入 pending/ 扫描逻辑（详见 2026-04-27 修复）
- 时间：2026-04-27 | 贡献者：Hermes总管

## [联邦架构] Pending 文件残留导致"幽灵任务"
- 现象：pending 文件状态改为 done 后未被物理删除，Cron 再次触发时可能被重复扫描（虽然有 status 校验，但文件堆积增加 IO）
- 解法：闭环后必须执行 `os.remove(pending_file)`，严禁保留已完成任务在 pending 队列
- 时间：2026-04-27 | 贡献者：Gemini架构审查

## [联邦架构] emit_result 时间戳混用 Unix Epoch / ISO 字符串
- 现象：`completed_at` 有时写 ISO 字符串，有时写 Unix Epoch，不统一
- 解法：统一使用 Unix Epoch（`int(time.time())`），超时判定和对撞最可靠
- 时间：2026-04-27 | 贡献者：Gemini架构审查

## [联邦架构] 僵尸任务死锁（status=processing 卡住）
- 现象：子 Agent 处理任务时中途崩溃，status 永远停留在 processing
- 解法：心跳超时重置 — 主 Agent 扫描时检测 `status==processing && locked_at > 30分钟`，强制重置为 waiting
- 时间：2026-04-27 | 贡献者：Gemini架构审查

## [联邦架构] V3.0.1-FINAL 最终协议三条军规
1. 原子性第一：严禁在未更新 `status: "processing"` 的情况下开始逻辑推理
2. Unix Epoch 唯一性：严禁使用任何 strftime/ISO 格式，全系统只认整数 Unix 时间戳
3. 结果归口：`emit_result()` 是唯一任务终结手段，未调用前严禁在群里回复「Done」
- 时间：2026-04-27 | 贡献者：Gemini架构审查

---

*最后更新：2026-04-27*
*触发规则：任务终结时（Success with Retry / Failure）提取坑点写入。日常任务无需更新。*
