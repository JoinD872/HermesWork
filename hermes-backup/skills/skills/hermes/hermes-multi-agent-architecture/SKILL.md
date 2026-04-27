---
name: hermes-multi-agent-architecture
description: Hermes 多 Agent 部署架构 — 当用户需要多个独立 Agent（不同人设/记忆/技能）时的规划和落地方法。核心限制：Hermes Gateway 单实例，不支持多 Profile 同时常驻。
category: hermes
---

# Hermes 多 Agent 部署架构

## 核心限制

**Hermes Gateway 是单实例** — 同一时刻只能有一个 gateway 进程运行。
- `hermes gateway` 启动时会检查是否已有实例在跑，报错 `"Gateway already running (PID N)"`
- 不支持 `--port` 或 `--profile` 参数来指定不同端口/配置
- 强行启动第二个会立刻退出

这意味着**无法让 5 个 Agent 的 gateway 同时常驻**。

### 跨平台 skill binding 机制差异（关键发现）

| 平台 | per-topic/channel skill binding | 实现位置 |
|------|-------------------------------|---------|
| **Telegram** | ✅ 有 `extra.dm_topics: [{name, skill, icon_color}]` | `telegram.py:246`（DM Topics 完整实现）|
| **Feishu** | ❌ **无原生支持** | 飞书 adapter 代码中无对应机制 |

**结论**：Telegram 可原生实现"不同群聊 topic → 不同 skill"，飞书需要用 prompt engineering 做意图路由。

### Profile 热重载机制

Gateway 支持通过 `HERMES_HOME` 环境变量加载不同 profile：

```bash
HermesHome=/root/.hermes/profiles/game-designer hermes gateway
```

`gateway.json` 路径随之变化为 `$(HERMES_HOME)/gateway.json`，session 目录也隔离。

### Session 隔离机制（Feishu）

Feishu session key 构建（`feishu.py:2824`）支持 `thread` 级别隔离：
- 单聊：`feishu:user:{open_id}`
- 群聊：`feishu:group:{chat_id}`
- 群内 thread：`feishu:thread:{thread_id}:{chat_id}`

**关键结论**：不同飞书群天然对应不同 session 目录，记忆不会串。但 personality（SOUL.md）需要靠主 SOUL.md 路由规则注入。

### Feishu per-group 访问控制（group_rules）

Feishu adapter 支持 `group_rules` 配置（`feishu.py:328`），可在 `config.yaml` 的 `extra` 中设置：

```yaml
extra:
  group_rules:
    oc_5a883cbe523b1a93ee269bba2f8536a0:
      policy: allowlist  # 或 "blocklist"
      allowed_users: []  # 留空=仅允许机器人
  default_group_policy: allowlist
```

这只控制**谁能和机器人说话**（白名单/黑名单），不负责路由 persona。

### Feishu 无原生 per-channel personality 绑定

| 平台 | per-channel personality | 实现方式 |
|------|-------------------------|---------|
| Telegram | ✅ 原生 dm_topics | `extra.dm_topics: [{name, skill, icon_color}]` |
| Feishu | ❌ 无原生支持 | 需在主 SOUL.md 通过 chat_id 判断注入 persona |

---

## ✅ 正确方案：channel_prompt 注入（已验证 2026-04-26）

**核心发现**：Gateway 单实例通过 `MessageEvent.channel_prompt` 字段实现 per-chat_id profile SOUL + memory 注入。Telegram/Discord adapter 早已使用此机制，Feishu adapter 需要手动补充。

**完整实现见**：`hermes-per-channel-profile-injection` skill

**关键代码位置**：
- `gateway/platforms/feishu.py` — 添加 `_resolve_profile_channel_prompt(chat_id)` 方法
- 3 处 `MessageEvent(...)` 构造处 — 添加 `channel_prompt=` 参数
- `gateway/run.py:9690-9695` — `combined_ephemeral` 拼接逻辑

**验证语法**：
```bash
cd ~/.hermes/hermes-agent && python -m py_compile gateway/platforms/feishu.py
```

**修改后必须重启 gateway**：
```bash
hermes gateway restart
```

---

### 方案 A：channel_prompt 注入（推荐 ✅）

单一飞书 Bot，通过 `channel_prompt` 字段在每次消息到达时注入对应 profile 的 SOUL + memory。

```
飞书消息 → FeishuAdapter
  → _resolve_profile_channel_prompt(chat_id)
  → 读取 ~/.hermes/profiles/<name>/SOUL.md + memories/MEMORY.md
  → 注入 MessageEvent.channel_prompt
  → Gateway 拼入 combined_ephemeral
  → AIAgent 收到完整 persona + 专业知识
```

**优点**：无需 delegate_task，实时注入，最低的延迟和 token 开销
**代价**：需要在 feishu.py 中维护 chat_id → profile 映射（硬编码或配置化）

### 方案 B：delegate_task 触发子 agent

主 SOUL.md 识别 chat_id → delegate_task → 子 agent 在独立 profile 下运行。

```
飞书消息 → Gateway (default profile)
  → 主 SOUL.md 识别 chat_id
  → delegate_task(goal="...", profile=vps-technician)
      → 子 agent 在 vps-technician profile 下运行
      → 读自己的 SOUL.md ✅ + memories/MEMORY.md ✅
  → 结果回到飞书
```

**缺点**：每条消息都触发子 agent，增加延迟和 token 消耗；且老V 需要主动说"我去查一下"才会触发

---

## ⚠️ 关键架构限制（2026-04-26 纠正）

### Gateway 永远只加载 default profile

```
Gateway 进程环境：
  HERMES_HOME = ~/.hermes（由启动时的环境变量决定）
  SOUL.md   → ~/.hermes/SOUL.md（全局，只有路由规则）
  MEMORY.md → ~/.hermes/memories/MEMORY.md（全局）

sub-profile 的文件根本不会被加载：
  ~/.hermes/profiles/vps-technician/SOUL.md      ← 不会被读 ❌
  ~/.hermes/profiles/vps-technician/memories/    ← 不会被读 ❌
```

证据（`agent/prompt_builder.py:945`）：
```python
soul_path = get_hermes_home() / "SOUL.md"  # 读的是 HERMES_HOME 下的路径
```

**结论**：方案 A（channel_prompt 注入）是唯一正确解法，直接绕过这个限制。

### `personalities` config 不是 per-chat_id 路由

`config.yaml` 里的 `personalities: {}` 是用于 `/personality` 命令切换内置人格的（如 `/personality pirate`），**不是 per-chat_id 路由机制**。

### 子 agent 的 memories 只在 delegate_task 时生效

只有通过 `delegate_task` 触发的子 agent 才会在自己的 profile 环境下运行（读自己的 SOUL.md + memories/）。Gateway 直接处理的飞书消息不走 delegate_task，所以所有群都用同一套全局记忆。

---

## 实际可用的多 Agent 方案

### 方案 A：多 Bot 多 Channel（推荐）

每个 Agent 绑定**独立的飞书自建应用**，各用独立飞书群/频道。

```
飞书 Bot A (App1) → game-designer profile
飞书 Bot B (App2) → UE5 profile
飞书 Bot C (App3) → health profile
飞书 Bot D (App4) → parenting profile
飞书 Bot E (App5) → researcher profile
```

**限制**：需要多个飞书自建应用（每个企业可创建多个）

**内存**：每个 gateway 实例 ~150-350MB，多 Bot = 多实例，但 Hermes 只允许单实例。

> ⚠️ 所以即使有多 Bot，gateway 单实例也只能连接一个 Bot。要真正多 Bot 运行，需要：
> 1. 运行多个独立的 Hermes 进程（非 gateway 模式）
> 2. 或修改源码让 gateway 支持多 Bot 接入

### 方案 B：单 Bot 智能路由

单一飞书 Bot，Agent 根据消息内容**判断类型**后路由到对应 profile/session 处理。

```
用户发消息 → Hermes (default profile) 
  → 判断：策划？UE5？健康？育儿？
  → delegate_task → 对应 profile 的独立 task
  → 结果统一回到飞书
```

- 各 profile 的 session 存在各自目录
- 凌晨研究员用 cron 触发，跑完即停
- 健康/育儿按需启动

**内存占用**：极低，只有常驻的一个 gateway

**缺点**：sub-agent 由主 gateway 进程代理，非真正独立 agent

### 方案 B（已纠正）：主 SOUL.md 路由 + delegate_task 强制加载 sub-profile

**关键修正：只有通过 delegate_task 触发的子 agent 才会真正加载 sub-profile 的 SOUL.md + memories/**。Gateway 直接处理的飞书消息不行。

```
飞书消息 → Gateway（default profile）
  → 主 SOUL.md 识别 chat_id
  → delegate_task(goal="处理 VPS 问题", profile=vps-technician)
      → 子 agent 在 vps-technician profile 下运行
      → 读 ~/.hermes/profiles/vps-technician/SOUL.md ✅
      → 读 ~/.hermes/profiles/vps-technician/memories/MEMORY.md ✅
  → 结果回到飞书
```

**落地步骤变更**：
- 主 SOUL.md 路由规则不变
- 每个群的处理不再是"直接响应"，而是"触发对应 sub-agent"
- sub-agent 用 `HermesHome` 环境变量或 profile-aware path 读自己的 soul + memory

> ⚠️ 这样每个群消息都会触发一个 delegate_task，增加延迟和 token 消耗。

### 方案 C：多 Bot（唯一真正隔离方案）

每个飞书 Bot（自建应用）对应一个 profile，跑独立的 Hermes Gateway 实例。

```
飞书 Bot A (App1) → profile: game-designer → gateway 进程 A
飞书 Bot B (App2) → profile: ue5         → gateway 进程 B
飞书 Bot C (App3) → profile: health       → gateway 进程 C
飞书 Bot D (App4) → profile: vps-technician → gateway 进程 D
```

**实现方式**：systemd 服务管理多个 gateway 进程，每个用不同 `HERMES_HOME`：
```bash
HermesHome=/root/.hermes/profiles/vps-technician hermes gateway
```

**限制**：需要多个飞书自建应用 token；多进程内存（约 150-350MB/个）。

---

## 推荐：方案 B 落地步骤（精化版）

**飞书多 Channel 架构：单 Bot + chat_id 路由 + delegate_task**

### 架构图

```
飞书群A（策划） ─┐
飞书群B（UE5）  ─┤
飞书群C（健康）  ─┼──→ Hermes Gateway（单实例）
飞书群D（育儿）  ─┤    chat_id 路由到独立 session
                ──┘    delegate_task 触发子 agent
```

**关键机制**：
1. **Session 隔离**：不同飞书群/频道 → 不同 session 目录（feishu.py 天然支持）
2. **Persona 注入**：主 SOUL.md 写路由规则，根据 chat_id 加载对应人设描述
3. **子 Agent 执行**：`delegate_task` 启动独立子 agent，读各自 profile 的 memories

### Step 1：规划 Agent

| Agent | Profile | 常驻? | Cron | 飞书群 |
|-------|---------|-------|------|--------|
| 游戏策划助手 | game-designer | ✅ | — | 策划群 |
| UE5 精通助手 | ue5 | ✅ | — | UE5技术群 |
| 健康助手 | health | ❌ 按需 | — | 健康群 |
| 育儿助手 | parenting | ❌ 按需 | — | 育儿群 |
| 凌晨研究员 | researcher | ❌ | 每天 03:00-07:00 | 凌晨研究员群（oc_ec9adb3139cd38ac706cd7a54c4d059d） |

**飞书群 chat_id（已接入）：**
- 策划群：`oc_5a883cbe523b1a93ee269bba2f8536a0`（游戏制作组，2026-04-21 更新）
- 健康群：`oc_6dbf15aa718c29adca8d085017930a71`

**飞书 group_rules 配置示例**：

```yaml
extra:
  group_rules:
    oc_5a883cbe523b1a93ee269bba2f8536a0:
      policy: allowlist
      allowed_users: []
    oc_5a883cbe523b1a93ee269bba2f8536a0:
      policy: allowlist
      allowed_users: []
    oc_6dbf15aa718c29adca8d085017930a71:
      policy: allowlist
      allowed_users: []
  default_group_policy: allowlist
```

### Step 2：主 SOUL.md 路由规则

主 profile（飞书 Bot 的默认 profile）的 SOUL.md 写入 chat_id 路由规则，**但注意**：Gateway 直接响应时只能用 prompt 描述人设，sub-profile 的专业知识只有走 delegate_task 才能真正加载。

```markdown
## 路由规则

当收到消息时，根据 chat_id 判断：

- 若来自 VPS 技术群（oc_cc9c8289c9520ff326578703ff17392c）
  → 以老V persona + delegate_task 触发 vps-technician profile 处理
- 若来自策划群 → 以 game-designer persona 响应
- 若来自健康群 → 以 health persona 响应

详细专业知识在各自 profile 的 memories/ 目录，通过 delegate_task 加载。
```

### Step 3：创建 Profile

```bash
hermes profile create game-designer --clone default
hermes profile create ue5 --clone default
hermes profile create health --clone default
hermes profile create vps-technician --clone default
```

每个 profile 有独立：
- `SOUL.md`（人设）
- `memories/`（记忆文件）
- `skills/`（技能目录）
- `config.yaml`（配置）
- `.env`（API key）

> ⚠️ **重要**：这些文件只在 `delegate_task` 时才被加载。Gateway 直接处理时读的是 default profile 的全局文件。

### Step 4：配置人设和记忆

每个 profile 的 `SOUL.md` 写入角色定义，**专业知识写进 memories/MEMORY.md**（不是 SOUL.md）。这样 delegate_task 触发时子 agent 能读到。

### Step 5：凌晨研究员 Cron

用 cronjob 工具，schedule `0 3 * * *`：
1. 读取所有 profile memories/pending.md
2. 深度搜索研究
3. 更新各 pending.md + 研究结论

使用 `HermesHome=/root/.hermes/profiles/researcher hermes chat` 在独立进程中跑研究任务。
```

---

## Profile 目录结构

```
~/.hermes/profiles/
  game-designer/
    SOUL.md          # 人设
    memories/
      project.md     # 项目基本信息
      preferences.md # 策划偏好
      rejected.md    # 已否决方案
      pending.md     # 待解决问题队列
    skills/          # 可放专属技能软链接
    config.yaml
    .env
  ue5/
  health/
  parenting/
  researcher/
```

---

## 记忆文件规范（各 Agent 通用）

每个 profile `memories/` 目录：
- `USER.md` — 用户基本信息（从 MEMORY.md 同步）
- `pending.md` — 当前未解决问题，研究员处理后更新
- `<topic>.md` — 各主题详情

---

## 已知问题

1. **gateway 单实例** — 最核心限制，需在架构设计阶段纳入考量
2. **飞书无原生 per-channel skill binding** — Telegram 有 dm_topics 机制实现不同 topic → 不同 skill，飞书没有对应实现，需靠 prompt engineering 做意图路由
3. **MCP 配置需同步** — 每个新 profile 的 config.yaml 要手动加入 `mcp_servers` 才能使用 MCP 工具
4. **skills 同步** — `hermes profile create --clone` 会同步 bundled skills，但自定义技能需手动创建目录
5. **delegate_task 子 agent 共享 gateway** — 子 agent 通过 `delegate_task` 启动，非真正独立进程，但可用独立 profile 的 memories

---

## 知识共享规则（小研必须遵守）

> 研究不共享 = 白研究。各 Agent 记忆目录天然隔离，必须主动推送。

| 研究类型 | 共享目的地 |
|---------|-----------|
| AI/UE5/游戏开发相关 | 游戏制作组（oc_5a883cbe523b1a93ee269bba2f8536a0） |
| 心理学、营养学、医学相关 | 健康群（oc_6dbf15aa718c29adca8d085017930a71） |
| AI 工具提效相关 | DM 发给小H 总管（oc_8391fa2b38acbd759ff75ab3616d5d1f） |
| 其他/无法归类 | DM 发给小H 总管（oc_8391fa2b38acbd759ff75ab3616d5d1f） |
| 凌晨研究员研究成果 | 凌晨研究员群（oc_ec9adb3139cd38ac706cd7a54c4d059d） |

小H 本身分管 AI，是各 sub-agent 的知识汇聚点。

---

## 飞书群免 @（已确认可实现 ✅）

设置 `FEISHU_REQUIRE_MENTION=false` 即可，无需改源码。详见 `hermes-feishu-troubleshooting` skill。

**对专用 sub-agent（如老V）的影响**：`FEISHU_REQUIRE_MENTION=false` 是**全局**设置，不支持 per-group 控制。若老V 独占一个群，可以全局开启免@；若其他群需要保留 @mention，则不适用。

可选替代方案：
1. **老V 独占群**（推荐）：全局免@，老V 在自己群里免@响应
2. **DM 替代**：sub-agent 收飞书 DM（DM 天然免@）
3. **用户改习惯**：在群里 @sub-agent

---

## 验证方法

创建 profile 后验证：
```bash
hermes profile list                          # 确认 profile 存在
cat ~/.hermes/profiles/<name>/SOUL.md        # 确认人设
cat ~/.hermes/profiles/<name>/config.yaml    # 确认配置
ls ~/.hermes/profiles/<name>/memories/       # 确认记忆目录
```

**但注意**：以上文件在 Gateway 直接处理时不会被加载。验证 sub-profile 记忆是否真正生效的方法：

1. 在飞书群发消息 → 观察 Gateway 日志确认走的是哪个 session
2. 用 `delegate_task` 测试子 agent，看它能否读到 sub-profile 的 memories
3. 检查 `~/.hermes/sessions/` 下的 session 目录，确认不同 chat_id 有不同 session

**诊断老V为什么不读自己 memory**：
```bash
# 老V的 memory 文件存在，但 Gateway 从不加载它
cat ~/.hermes/profiles/vps-technician/memories/MEMORY.md   # 有内容 ✅
cat ~/.hermes/memories/MEMORY.md                              # 全局，只有通用记忆

# Gateway 进程使用的 HERMES_HOME
cat /proc/$(pgrep -f "hermes gateway")/environ | tr '\0' '\n' | grep HERMES_HOME
# 输出通常是 ~/.hermes，不是 ~/.hermes/profiles/vps-technician
```
