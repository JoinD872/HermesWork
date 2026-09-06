# 逆向工作规范

> 适用环境：E:\Opencode\MXD\逆向_纯净
> 生效日期：2026-09-05
> 替代文件：原 GLOBAL_WORK_BEHAVIOR.md / WORK_BEHAVIOR.md 中的冲突/过时规则

---

## 0. 协作流程与完成状态

本文件与上级 [`AGENTS.md`](../AGENTS.md)、本目录 [`AGENTS.md`](AGENTS.md) 共同生效。上级文件规定统一协作原则，本文件规定逆向纯净环境的专业边界。

### 0.1 任务边界

每轮分析开始前必须明确：

```text
【本轮目标】
【输入文件和版本】
【允许产出】
【禁止修改或操作】
【证据要求】
```

分析过程中发现输入、地址、类结构或已有结论与任务描述不一致时，先记录差异和证据，不得静默改写原始资料。

### 0.2 完成状态

```text
实现完成 → 验证通过 → 用户验收
```

逆向分析中的“实现完成”指分析产出已经写入正确目录并有可追溯提交；“验证通过”指证据对应同一个提交、同一输入版本和同一分析环境；“用户验收”指用户确认该产出满足分析目标。GPT 只能给出建议，不代替用户宣布最终验收。

### 0.3 版本一致性

提交版本、输入文件版本、运行环境和验证证据必须保持一致。提交后又产生未提交修改时，后续结果不得直接证明之前提交有效，除非明确证明使用的仍是之前的提交版本。

## 1. 启动必读

| 序号 | 文件 | 用途 |
|------|------|------|
| 1 | ../AGENTS.md | 统一协作规则 |
| 2 | AGENTS.md | 逆向纯净局部边界 |
| 3 | README.md | 目录结构 + 已知结论 + 工具指南 |
| 4 | 01_dump/new_analysis.md | 漂移校验 + 类定位 + 候选排除逻辑 |
| 5 | 01_dump/new_classes.json | 5个关键类偏移（character/camera） |
| 6 | 02_pseudo/README.md | 反作弊伪代码索引 |
| 7 | 04_packet/F1_key.md | 协议分析现状 + 阻塞点 |
| 8 | CODEX_STATUS.md | 当前分析阶段、已确认内容和阻塞项 |
| 9 | WORK_RULES.md | 本文件 |

---

## 2. 纯净边界（核心规则）

本环境**只接受逆向分析产出**，不接受其他任何内容。

| 操作 | 允许 | 说明 |
|------|------|------|
| 写入逆向分析产出（新dump、新分析报告、纠正已有结论） | ✅ | 本环境的唯一用途 |
| 读取已有逆向数据 | ✅ | 正常分析 |
| 写新文件追加纠正（不改原文件） | ✅ | 纠正写新文件，原文件保留 |
| 删除/覆盖已有逆向数据 | ⚠️ 仅追加 | 原始dump/数据文件不可变 |
| 写入Bot代码、YOLO模型、配置文件 | ❌ | 逆向环境不接受非逆向内容 |
| 写入日志/备份/调试截图 | ❌ | 非逆向内容 |

**识别标准**：文件内容是否帮助理解游戏内部结构/协议/反作弊机制。是→可以放，不是→不能放。

### 2.1 分析资源与进程管理

- 静态分析默认使用 DLL、metadata、dump 和资源包的离线副本；不读取运行中游戏进程内存。
- 任何超过 100MB 的文件都禁止使用 `$lines = Get-Content 文件`、`Get-Content -Raw` 或等价的整文件读取；特别是 `mxd-core-objdump.txt`，只能使用流式 `rg`、有限 `rg -A/-B` 或按偏移/行号分块读取。
- 巨型反汇编应先建立地址/行号索引，再按需读取局部范围；同一轮任务不得让多个进程重复整文件扫描同一个输入。
- 单次分析命令必须有明确超时、有限输出和可追踪的任务标签；出现超时、内存异常增长或进程未退出时，立即进入清理路径。
- 启动 `pwsh`、`rg`、Python、DXBC 渲染器或其他外部分析程序时，必须记录根 PID 和子 PID；优先通过 `挂机工具/scripts/run_scoped_analysis.ps1` 启动。
- 单个分析进程工作集达到或超过十进制 1,000,000,000 字节时，立即停止该进程并报告 PID；不得使用 PowerShell 的二进制 `1GB` 字面量代替该阈值。
- 只结束本轮分析明确创建且已确认的孤立分析进程；不得结束游戏进程、反作弊进程或未知进程来“清理内存”。
- 正常完成、失败、超时或用户取消时，都必须通过 `try/finally` 回收本轮创建的进程，并删除本轮临时目录；不得留下后台分析进程。
- 临时副本和反汇编中间产物放在系统 TEMP 或明确的临时目录；源文件、原始 dump 和已交付证据不可因清理而删除。
- 每次重型分析后必须确认：本轮创建的进程是否全部退出、是否还有匹配本轮标签的 `pwsh`/`rg`/Python/渲染器、临时目录是否已删除、清理后任务进程内存是否恢复为 0；任一项未通过，不得开始下一轮。

强制验收字段至少包括：

```text
STARTED_PID=
TRACKED_PROCESS_IDS=
MEMORY_LIMIT_BYTES=1000000000
PEAK_WORKING_SET_BYTES=
CLEANUP_CREATED_PROCESSES=COMPLETE
CLEANUP_TEMP_DIRECTORY=COMPLETE
POST_CLEANUP_TRACKED_PROCESS_MEMORY_BYTES=0
POST_CLEANUP_MEMORY_STATUS=RESTORED
RESIDUAL_MATCHING_PIDS=NONE
ANALYSIS_STATUS=
```

如果出现残留 PID、清理后内存未恢复、输出排空超时或根进程退出等待超时，必须先报告并处理，不能把任务标记为完成。

---

## 3. 解决问题的流程（GitHub优先）

收到任务后，先判断任务风险和是否依赖外部方案。对已有证据的局部核对可以直接执行；涉及新工具、新格式、新分析链路或架构选择的 L2/L3 任务，必须先搜索并评估成熟方案，再确定分析方式。不得在没有足够证据时把推测写成确认结论。

### 第一步：搜索成熟方案

| 搜索目标 | 推荐仓库 | 关键词 |
|----------|----------|--------|
| IL2CPP运行时分析 | vfsfitvnm/frida-il2cpp-bridge | frida il2cpp runtime |
| IL2CPP字段发现 | dwgx/vrchat-il2cpp-re | obfuscated field names recovery |
| IL2CPP元数据解析 | SamboyCoding/Cpp2IL | il2cpp metadata analysis |
| 反反作弊绕过 | 已知：ScyllaHide | ScyllaHide BlackCipher |
| 协议解密 | 已知：maple_crypto | maplestory packet crypto |
| MCP辅助分析 | axhlzy/il2cpp-frida-mcp | il2cpp frida mcp ai |

使用 `websearch` 搜索 `GitHub [关键词] 2025 2026`，获取最新方案。

### 第二步：评估方案适用性

| 评估项 | 说明 |
|--------|------|
| 目标环境 | Unity 6000.3.16f1 / IL2CPP v39 / Windows x64 |
| 反作弊兼容 | BlackCipher (SDGame32.sys) 是否检测该方案 |
| 已有数据能否复用 | 方案输出是否能与 dump.cs / il2cpp.h 对接 |

### 第三步：执行或推理

| 情况 | 做法 |
|------|------|
| 有成熟方案且适用 | 评估后集成，产出标 V（Validated） |
| 有方案但需改造 | 改造后集成，产出标 C（Candidate） |
| 无成熟方案 | 基于已有数据推理，产出**必须标 C**，禁止标 S |

### 禁止

- 对需要外部方案或新分析链路的任务跳过搜索直接推理
- 未经搜索就宣称"没有现成方案"
- 搜索了但没看结果就推理

### 3.1 GitHub 网络与推送规范

- GitHub 的 clone、fetch、pull、push 和 `ls-remote` 默认必须沿用本机现有代理配置；不得为了“测试直连”在实际 Git 操作中清空 `http.proxy`、取消 `HTTP_PROXY/HTTPS_PROXY` 或改走未经验证的网络路径。
- 若需要诊断直连，只允许做只读连通性测试，不能用直连结果替代实际推送路径。
- 推送前先确认本地 `HEAD`、目标分支和远端地址；推送后必须用 `git ls-remote` 核对远端分支哈希与本地提交哈希一致。
- 出现超时、断开或 RPC 错误时，不得据此判断“已上传”；先查询远端哈希，再使用原有代理路径重试。
- 代理、令牌和凭据只用于连接，不得输出到报告、日志或聊天内容。

---

## 4. 安全红线

| 规则 | 说明 | 违反后果 |
|------|------|----------|
| **不碰进程** | 禁止对 Maplestory_Classic.exe 执行 OpenProcess / ReadProcessMemory / WriteProcessMemory / CreateRemoteThread | 立即终止 |
| **只读离线** | dump/分析基于文件静态副本，不触碰运行中进程内存 | 立即终止 |
| **主号隔离** | 所有动态操作（Frida/注入/发包）必须在隔离VM + 影子账号中执行 | 立即终止 |
| **高危串行** | BlackCipher/驱动级操作单独隔离，需二次确认 | 暂停等待 |

### 4.1 NonFinite / AntiMacro 专项边界

- `UIAntiMacroNonFinite` 只做静态离线还原、资源核对和伪代码审查。
- 不实现自动鼠标轨迹、RawInput 模拟、PointerEventData 注入、成功/失败标志修改、结果包伪造或自动提交。
- “检测到测谎后杀进程并自动重连”不视为可靠规避方案；文档和工具设计应优先记录、停止自动输入并保留证据。
- 任何运行时验证都必须先明确目标、范围和回滚方式；涉及进程、驱动、注入或发包的内容默认不执行。

---

## 5. 数据可靠性分级

### 5.1 NonFinite 专项统一口径

`UIAntiMacroNonFinite` 报告统一使用以下两层标记：

- 报告总体可靠性：`C`（当前以离线静态证据为主）。
- 单条技术结论：`CONFIRMED`、`STRONG_INFERENCE`、`UNKNOWN`。

其中 `UNKNOWN` 必须注明已经覆盖的搜索范围和仍缺失的证据。不得把“高把握度/中等把握度/尚未确认”或 `S/V/C/H` 与上述单条结论混用。

### 5.2 历史/结构标签

| 级别 | 标记 | 含义 | 示例 |
|------|------|------|------|
| **S** | Stable | 漂移校验通过，偏移未变 | character ti=1200 所有字段 |
| **V** | Validated | 运行时验证确认（Frida/内存读取） | 待获取 |
| **C** | Candidate | 静态分析推测，未经运行时验证 | MonoBehaviour子类→怪物候选 |
| **H** | Hashed | 字段名被哈希混淆，仅知类型和偏移 | dump.cs中绝大多数字段 |

> `S/V/C/H` 仅保留给历史漂移、结构或跨项目标签；不用于替代 NonFinite 的 `CONFIRMED / STRONG_INFERENCE / UNKNOWN`。其他历史报告若继续使用，必须在上下文中说明其标签体系。

---

## 6. 并行规则

### 判断是否并行

| 场景 | 做法 |
|------|------|
| 单文件读取 / 单条grep / 单行命令 / 单文件编辑 | **直接做**，不动用子代理 |
| 2+ 个互不依赖的独立搜索/分析/任务 | **并行**，拆子代理同时执行 |
| A的结果决定B的输入 | **投机并行**：B用旧数据先跑，A出结果后补delta |

### 代理数量

| 任务规模 | 代理数 | 说明 |
|----------|--------|------|
| 2-3个独立任务 | 2-3 | 如同时搜grep+读文件+看文档 |
| 4-8个独立任务 | 4 | 高影响分析，如多方向类定位 |
| 8+ 个独立任务 | 8（上限） | 全量扫描，如16845类分类 |

### 执行原则

1. 一转多发：拆分后立即并发发射多个Task
2. 独立产出：每个子代理写独立目录或独立文件
3. 主代理汇总：最后统一整合，标注冲突
4. 高危串行：BlackCipher/驱动/注入等不与并行池混跑

---

## 7. 目录规范

```
逆向_纯净/
├── 01_dump/              不动（原始dump数据只读）
├── 02_pseudo/            不动（反作弊伪代码只读）
├── 03_assets/            不动（地图数据只读）
├── 04_packet/            可追加协议分析
├── 04_shader/            可追加shader分析
├── 05_data/              可追加游戏数据文档
├── 06_runtime/           新增：运行时分析产出
│   ├── scripts/          Frida脚本
│   └── evidence/         验证截图/日志
├── analysis/             新增分析报告放这里
└── 资源包/               不动
```

### 新增产出放置规则

| 产出类型 | 放置位置 |
|----------|----------|
| Frida脚本 | `06_runtime/scripts/` |
| 分析报告 | `analysis/` |
| 验证证据（截图/日志） | 对应目录的 `evidence/` |
| 纠正已有结论 | 写新文件到对应目录，不改原文件 |
| 新的dump | `01_dump/`（追加，不覆盖） |

### 禁止

- 在根目录放散文件（STATUS.md / benchmark.json / raw.txt 等）
- 在已有目录里放不相关的内容
- 覆盖原始dump/数据文件

---

## 8. 输出规范

### 分析报告

```
# [编号] [标题]
> 日期：YYYY-MM-DD
> 输入：[文件路径]
> 方法：[分析方法] + GitHub方案参考：[仓库链接]
> 可靠性：C
> 单条证据状态：CONFIRMED / STRONG_INFERENCE / UNKNOWN

## 发现
...

## 证据
- 截图/数据：[路径]

## 下一步
...
```

### 代码产出

| 类型 | 位置 |
|------|------|
| Frida脚本 | `06_runtime/scripts/` |
| 分析脚本 | `analysis/` |
| 验证报告 | 对应目录的 `evidence/` |

### 证据留存

- 截图：before / after 成对
- 日志：带时间戳
- 指标：json格式，含输入参数

---

## 9. 工具链

### 已安装

| 工具 | 路径 | 用途 | 注意事项 |
|------|------|------|----------|
| Il2CppDumper v39 | `%TEMP%\Il2CppDumper-v39\Il2CppDumper.exe` | IL2CPP dump | 需先改config.json: `RequireAnyKey: false` |
| dnSpy / ILSpy | 手动 | 浏览DLL | 打开 `01_dump/il2cppdump/Assembly-CSharp.dll` |
| Ghidra | 手动 | 静态反汇编 | 用 `script.json` 生成导入脚本 |

### GitHub参考方案

| 工具 | 仓库 | 用途 | 状态 |
|------|------|------|------|
| frida-il2cpp-bridge | vfsfitvnm/frida-il2cpp-bridge | 运行时dump/trace/heap扫描 | 待集成 |
| il2cpp-frida-mcp | axhlzy/il2cpp-frida-mcp | AI辅助IL2CPP分析 | 待集成 |
| VRChat RE管线 | dwgx/vrchat-il2cpp-re | 哈希字段名恢复 | 参考价值 |
| il2cpp-dumper-rs | rodroidmods/il2cpp-dumper-rs | Rust版dump | 备选 |

---

## 10. 版本更新流程

当 GameAssembly.dll / global-metadata.dat 变化时：

1. 用 Il2CppDumper 重新 dump（30秒）
2. 与旧版 `drift_report.json` 对比偏移变化
3. 标注新漂移项为 unstable
4. 更新 `new_classes.json` 和 `new_analysis.md`
5. 所有之前标 S 的结论需重新验证

---

## 11. 禁止事项

| 禁止 | 原因 |
|------|------|
| 修改 dump.cs / il2cpp.h / script.json / stringliteral.json | 原始数据不可变 |
| 在主号环境执行 Frida / 注入 / 发包 | 反作弊封号风险 |
| 删除其他AI的产出 | 保留完整分析链 |
| 未验证就将 C（candidate）标为 S（stable） | 误导后续分析 |
| 全量 Read >100MB 文件到内存 | 可能造成数 GB 级内存占用；必须搜索定位后分段读取 |
| 重型分析后不检查进程 | 可能留下孤立的高占用 PowerShell/分析器进程 |
| 用结束游戏/反作弊进程的方式清理资源 | 破坏测试环境并增加账号/系统风险 |
| 跳过启动必读直接开工 | 缺乏上下文导致重复劳动 |
| 写入与逆向无关的文件 | 污染纯净环境 |
| 对需要外部方案或新分析链路的任务跳过搜索直接推理 | 容易重复造轮子或把未知内容写成结论 |
| 覆盖原始逆向数据文件 | 不可逆破坏 |
