# [ARCHITECTURAL PRE-SPLIT BLUEPRINT]
# 触发阈值：MEMORY.md > 300 Lines 或 Token 基础开销过高
# 1. MEMORY_RULES.md（核心宪法）-> 强制注入（P0）：任务规范/双写逻辑/影子工单/P3协议
# 2. MEMORY_ENV.md（环境清单）-> 按需读取（P1）：浏览器配置/出口IP/群ID/故障记录
# 3. MEMORY_KNOWLEDGE.md（动态知识库）-> 仅限Grep（P2）：实战坑点归档（严禁全量载入上下文）

## 任务规范
多步骤任务：每步完成后立即写入，不等 reset。双写：Memory + ~/.hermes/task_checkpoint.json。Reset 重连后必须发飞书通知。
§
## 浏览器环境
- agent-browser v0.26.0 + Chrome 147，playwright v1.58.0，camoufox 0.4.11 已装（Firefox 内核）
- VPS 出口 IP（洛杉矶 HostPapa）被百度/知乎屏蔽，bilibili ✅ 可访问
- SearXNG（localhost:8888）搜索 ✅ 正常
§
## 用户期望
- 给链接后直接整理完整内容，不需要他自己点
- 信息要完整详细，不接受粗略摘要
- "你去验证一下" = 自己验证完再汇报，不让大佬再操作
- "先彻底关掉它" = 立即执行，不拖
§
## 图片识别（MCP）
- vision_analyze 已禁用
- 图片理解统一走 MMX CLI：mmx vision describe <图片路径>
- mmx-cli v1.0.11，认证信息已存独立 credential store
- ⚠️ MiniMax MCP 有平台级 bug（1004 login fail），不要用，统一走 MMX CLI
§
## 联邦能力画像（2026-04-26）
> 路由决策最高参考依据。通过 Webhook 实现跨群主动推送（2026-04-27 已打通）。

### Webhook URL 配置（2026-04-27 实测可用）
| Agent | Webhook URL |
|-------|------------|
| 小研 | https://open.feishu.cn/open-apis/bot/v2/hook/20acd1d4-fe75-404e-ac5e-5e49bc5c587b |
| 小健 | https://open.feishu.cn/open-apis/bot/v2/hook/00394231-ecf8-4e00-9a9b-50fc747d44bd |
| 小策 | https://open.feishu.cn/open-apis/bot/v2/hook/fd3ea207-82cf-4e19-a134-45926df90c0b |
| 老V | https://open.feishu.cn/open-apis/bot/v2/hook/9fa84937-aa99-4c18-93f2-a0736dcf86fa |
| 获取方式：飞书群 → 设置 → 应用与机器人 → 添加机器人 → 自定义机器人 → 复制 Webhook URL |

### 小研（凌晨研究员 · oc_ec9a）
**搜索深度：** Arxiv论文/GitHub Repo/专业论坛/Reddit
**输出标准：** 技术综述（架构演进+论文解读）/ 竞品分析（vLLM vs TGI等）/ 数学推导；格式：结论先行→背景→详细发现→应用建议→参考来源
**【不处理】** 非AI/ML领域 · 实时新闻/股价 · 代码实现（只出设计思路）· 长文本直出（深度优先，每报告聚焦单一主题）
**【路由补充】** 给小研的任务应分步骤索取，不要一次性要长文本；每轮聚焦单一主题
**【任务派发规则】** DM 消息不自动触发排队，必须显式说"写入 pending.md"；低优先级任务也应用此规则
**【任务闭环机制】** 小研不主动回复 Done；任务是否完成需用户去群里主动确认，bot 通信本身正常但无自动回执

### 小健（健康顾问 · oc_6dbf）
**知识覆盖：** 颈椎/腰椎/RSI、20-20-20眼疲劳、睡眠管理、饮食建议、运动处方、心理健康
**诊断逻辑：** 症状预排查（持续时间/诱因/缓解因素）→ 判断亚健康vs就医指征；饮食红黑榜（胃炎用户）
**【医学红线】** 必须建议去医院的场景：胸痛/呼吸困难/剧烈头痛/晕厥/出血/骨折/持续高热等急症
**【路由补充】** 路由健康问题时，优先展示小健的医学红线，防止AI误导

### 老V（VPS技术 · oc_cc9c）
**核心专长：** 隧道代理（JoinD CF Tunnel/Xray/VLESS+WS）、网络安全（UFW/fail2ban/SSL）、Docker/容器管理、VPS全生命周期（ RackNerd Debian/Ubuntu）
**常用工具：** ss/lsof/netstat · nginx -t · systemctl · docker ps/logs · curl -I
**【局限性】** 不操作域名/DNS业务 · 不写业务代码 · 不部署数据库 · 仅支持Linux VPS · 不处理中国内地网络优化（已知IP被屏蔽无解）
**【路由补充】** Windows VPS 问题直接拒，不转发；已知IP屏蔽问题（百度/知乎）告知用户无解

### 小策（游戏制作 · oc_5a883c）
**引擎/语言：** UE5（蓝图/C++/Slate/UMG/Chaos/Nanite/Lumen/网络同步/World Partition）、GLSL Shader、Python工具链
**设计专长：** 玩法设计（Core Loop/攻防博弈）、数值框架（属性公式/成长曲线/经济通胀）、叙事结构、商业化（F2P/季卡/战斗通行证）、关卡设计
**【不负责】** 完整项目代码文件输出 · 团队分工排期 · 代码review

 §
## 知识共享规则（P0）
新建 Agent 时，必须同步传递当前已验证的最优搜索方案，不能让新 agent 从零摸索。
§
## 当前最优搜索方案
1. SearXNG (localhost:8888) > mcp_searxng_search > 其他
2. Browser tool：Camoufox (Firefox) + Playwright (Chromium) 双引擎
§
## cron 时区
设置 cron 必须用用户当地时间（GMT+8）。凌晨3点触发 = cron 设 19:00 UTC。
§
## MiniMax 图片生成故障（2026-04-26 最终结论）
- API Key 绑定 cn region（global region 返回 code 1: invalid api key）
- cn region 图片 API 不可用：POST api.minimaxi.com/v1/image_generation 返回 code: 6
- 文本/对话 API 正常
- image.minimaxi.com 独立域名全局 DNS NXDOMAIN
- Cloudflare Worker 代理方案失败
- 默认绘图切换至 pollinations.ai（格式：https://image.pollinations.ai/prompt/<prompt>.png）
§
## Agent 共性缺陷
大佬 2026-04-25 反馈：遇到难点会死磕一条路不变通，搜索方式不会换，不会主动查官方文档/社区/GitHub Issues/Reddit。
§
## 联邦经验共创协议（V3.0-P3-Active）（2026-04-26）

所有 Agent（包括主 Agent）通用最高行为准则补丁。

### 1. 强制归档准则
- **触发逻辑**：任务结束后，若执行过程中遇到【报错、配置冲突、搜索 2 次以上才解决的难点】，禁止直接 Close
- **动作**：必须向 ~/.hermes/global_knowledge.md 贡献一条实战经验

### 2. 原子写入保护（Lock & Append）
- **检测锁**：检查 global_knowledge.lock 是否存在
- **重试逻辑**：若锁存在，随机等待 0.2s-0.5s 后重试，上限 3 次
- **上锁写入**：
  1. 创建锁文件，内容写入：[Agent名]_PID_[RandomID]
  2. 执行 Append（追加入文件末尾）
  3. 立即删除锁文件
- **降级处理**：若 3 次均失败，将经验标注 [PENDING_ARCHIVE] 附加在任务结果 summary 中，由主 Agent 手动归档

### 3. 经验归档模板（Strict Schema）
```
## [<领域标签>] <简练的坑点标题> / <核心关键字>
- 现象：<报错原文或异常行为描述>
- 解法：<验证有效的 CLI 指令、代码片段或逻辑操作>
- 时间：<YYYY-MM-DD> | 贡献者：<Agent名>
```
- 格式要求：严禁废话，只记录【坑点标题 + 核心原因 + 验证有效的解决方案】
§
## 飞书@机制根本限制（2026-04-26 发现）
群里发"[@小研]"是纯文本，非真正飞书@通知，不触发session唤醒。所有子Agent共享同一bot身份"Hermes总管"。真实@需从成员列表选人。V3.0-Trigger自启动协议因此失效。

## MiniMax图片理解API故障（2026-04-26）
mcp_minimax_plan_understand_image持续404（api.minimaxi.com/v1/v1/coding_plan/vlm）。图片理解不可用。
§
## 联邦 Cron Job ID 速查（2026-04-27）
- 老V: a259819c24f4（09:00 UTC / 17:00 GMT+8）
- 小研: ef20c63571f7（19:00 UTC / 03:00 GMT+8）
- 小健: a2d3c2998db3（11:00 UTC / 19:00 GMT+8）
- 小策: 5e3728b97221（21:00 UTC / 05:00 GMT+8）

## 联邦任务验证核心原则
验证 cron 任务是否真正执行了 federation 任务：检查 callback 文件 + pending 状态，不能只看 output md 文件或 `cronjob(run)` 返回值。

## cronjob(action='run') 行为（经验证）
- `success: true` 只表示触发器启动，不代表真正执行了新 prompt
- 真正验证：callback 文件存在 + pending 状态变 done
- `.tick.lock` 存在时手动 run 会被跳过（需先 rm）

## federation-callback-pool skill 已更新
V3.0.1-FINAL 协议 + 状态机 + 所有已知坑点已归档至 skill，无需重复摸索。
§
汇报联邦任务结果时，统一使用美化版格式（federation-result-beautifier skill）：emoji + 表格 + 结论先行 + ⏱时间戳。严禁直接贴原始 JSON 给用户。