# 挂机工具工作规范

> 适用环境：E:\Opencode\MXD\挂机工具
> 生效日期：2026-09-06

---

## 0. 协作流程与完成状态

本文件与上级 [`AGENTS.md`](../AGENTS.md)、本目录 [`AGENTS.md`](AGENTS.md) 共同生效。上级文件规定统一协作原则，本文件规定挂机工具的具体执行规则。

### 0.1 任务边界

每个代码任务开始前必须明确：

```text
【本轮目标】
【允许修改】
【禁止修改】
【验收标准】
【验证方式】
```

任务过程中发现方案与真实代码不一致时，先记录差异和原因，再按真实代码实现目标；不得为了服从旧方案而修改已经不存在或不相关的代码。

### 0.2 完成状态

```text
实现完成 → 验证通过 → 用户验收
```

- **实现完成**：有实际代码修改、文件清单和提交号。
- **验证通过**：证据绑定同一个提交号、运行环境/配置、测试或实机证据和实际结果。
- **用户验收**：用户实际确认效果符合目标。GPT 只能给出“建议验收”或“存在阻塞”。

如果提交后又有未提交修改，后续测试、日志、截图或录屏不得直接证明之前的提交有效，除非明确证明运行的仍是之前的提交版本。

### 0.3 风险分级

| 等级 | 典型任务 | 流程 |
|------|----------|------|
| L0 | 文案、注释、单个显示字段 | 检查后直接改并做基本验证 |
| L1 | 单文件普通问题 | 读取代码、修改、定向测试 |
| L2 | 状态机、导航、跨文件行为 | GPT 施工单 → Codex 检查方案 → 实现 → 测试 → 提交 → GPT 审查 |
| L3 | 核心架构、安全边界、跨模块重构 | 分支/PR → 实现 → 证据验证 → GPT 审查 → 合并 |

不要求所有任务都机械执行 Ask → Code → Review；由风险和影响范围决定。

## 1. 启动必读

| 序号 | 文件 | 用途 |
|------|------|------|
| 1 | ../AGENTS.md | 统一协作规则 |
| 2 | AGENTS.md | 挂机工具局部边界 |
| 3 | README.md | 项目说明 + 快速开始 + 架构 |
| 4 | yolo_gui/settings.json | 运行配置 |
| 5 | yolo_gui/app.py 第1-80行 | 主程序导入结构 |
| 6 | WORK_RULES.md | 本文件 |

---

## 2. 解决问题的流程（GitHub优先）

收到任务后，先判断任务风险和是否依赖外部方案。L0/L1 的局部修复可以直接检查现有代码并处理；L2/L3 或涉及第三方方案、架构选择的任务，必须先搜索并评估成熟方案，再确定实现方式。

### 第一步：搜索成熟方案

| 搜索目标 | 推荐关键词 |
|----------|------------|
| YOLO目标检测 | yolo onnx inference python opencv |
| 屏幕截图/窗口捕获 | windows screen capture python mss dxcam |
| 键盘输入模拟 | windows keyboard input interception sendinput |
| 图像识别/模板匹配 | opencv template matching python |
| 状态机设计 | finite state machine python game bot |
| GUI框架 | python tkinter gui 2025 |
| 断线重连自动化 | game auto reconnect bot image detection |
| 小地图定位 | minimap player position detection opencv |

使用 `websearch` 搜索 `GitHub [关键词] 2025 2026`。

### 第二步：评估方案

| 评估项 | 说明 |
|--------|------|
| 能否直接用 | 方案是否适配当前技术栈（Python 3.11 / opencv / onnxruntime） |
| 需要改造多少 | 改造成本是否低于从零写 |
| 逆向数据能否复用 | 是否需要逆向_纯净中的数据配合 |

### 第三步：实现或推理

| 情况 | 做法 |
|------|------|
| 有成熟方案 | 集成后验证，标注参考来源 |
| 有方案需改造 | 改造后验证，标注改造点 |
| 无成熟方案 | 基于已有代码和逆向数据推理，**产出必须标注"自主实现"** |

### 2.1 GitHub 网络与推送规范

- GitHub 的 clone、fetch、pull、push 和 `ls-remote` 默认必须沿用本机现有代理配置；不得为了“测试直连”在实际 Git 操作中清空 `http.proxy`、取消 `HTTP_PROXY/HTTPS_PROXY` 或改走未经验证的网络路径。
- 若需要诊断直连，只允许做只读连通性测试，不能用直连结果替代实际推送路径。
- 推送前先确认本地 `HEAD`、目标分支和远端地址；推送后必须用 `git ls-remote` 核对远端分支哈希与本地提交哈希一致。
- 出现超时、断开或 RPC 错误时，不得据此判断“已上传”；先查询远端哈希，再使用原有代理路径重试。
- 代理、令牌和凭据只用于连接，不得输出到报告、日志或聊天内容。

### 2.1.1 版本一致性与工作区

- 开始任务前检查当前分支、`HEAD`、远端和工作区状态。
- 已有未提交修改时，不得擅自 `reset`、`stash`、覆盖、格式化或提交这些修改。
- 只提交本轮任务产生的文件，不得混入任务外修改。
- 验证记录必须写明提交号、运行环境/配置、证据类型和实际结果。
- 提交后如果工作区再次变化，必须重新确认实际运行的版本；不能把新版本结果算给旧提交。

### 2.2 并行拆分规范

- 收到复合任务后，先拆成核心分析、实现修改、测试/对拍、文档发布等子任务。
- 没有写入冲突、且不互相依赖的子任务必须并行推进；例如静态逆向分析可以和视觉对拍、测试准备同时进行。
- 写代码前由主流程处理当前关键阻塞项；并行任务只接收边界清楚、输出可验收的工作，避免多个任务修改同一文件。
- 不为“看起来并行”而重复分析同一问题；子任务完成后只做一次结果汇总和冲突检查。
- 等待子任务时继续处理不依赖其结果的本地工作；禁止无结果地反复轮询。完成、失败或需要人工决策时再汇报。
- 并行任务同样遵守本文件的安全边界：只做离线/静态分析，不读取游戏进程、不注入、不模拟真实游戏输入、不伪造结果。

---

## 3. 逆向数据边界（只读）

挂机工具可以**读取**逆向_纯净的数据，但**不可写入**。

| 操作 | 允许 | 说明 |
|------|------|------|
| 读取逆向_纯净的地图/跳跃/协议数据 | ✅ | 跑图/平台归属等功能需要 |
| 在逆向_纯净中写入Bot相关文件 | ❌ | 逆向环境只接受逆向产出 |
| 在本项目中存放逆向数据副本 | ❌ | 直接读逆向_纯净，不复制 |
| 向逆向_纯净提交逆向发现 | ✅ | 按逆向_纯净的WORK_RULES执行 |

### 依赖的逆向数据

| 文件 | 用途 | 引用方式 |
|------|------|----------|
| `逆向_纯净/03_assets/new_map.json` | 705张地图平台数据 | platform_layer.py 读取 |
| `逆向_纯净/03_assets/jump_calib.json` | 跳跃校准参数 | platform_layer.py 读取 |

引用路径：通过 `os.path.join(os.path.dirname(_HERE), "逆向", "03_assets", ...)` 读取。

---

## 4. 目录规范

```
挂机工具/
├── src/                    所有源码（当前 yolo_gui/ → src/gui/）
│   ├── gui/                主程序（app.py + 各模块）
│   ├── infer/              推理引擎（yolo_infer.py + models + cudnn）
│   ├── train/              训练工具（labeler + trainer）
│
├── models/                 模型文件（只有当前使用的 .onnx）
├── data/                   数据集（训练帧/标注/地图索引/路线）
├── config/                 配置（settings.json / routes.json / classes.json）
├── docs/                   文档（README / CHANGELOG / 设计决策）
├── scripts/                启动脚本 / 打包脚本（run.bat / build.bat）
├── bin/                    构建产物（exe）
└── tmp/                    临时文件（随时可删）
    ├── logs/               运行日志
    ├── backup/             配置备份
    ├── debug/              调试截图
    └── verify/             验证输出
```

### 新增模块规则

| 场景 | 做法 | 错误做法 |
|------|------|----------|
| 加新功能模块 | `src/gui/新模块.py` | 在 app.py 里加500行 |
| 加新模型 | `models/模型名.onnx` | 在 yolo/ 根放 user_trial_xxx.onnx |
| 加新配置 | `config/配置名.json` | 在 settings.json 里加500行 |
| 跑图测试数据 | `data/routes/` | 在 yolo_gui/ 根放 route_xxx.json |
| 调试截图 | `tmp/debug/` | 在 yolo_gui/debug_shots/ 无限积累 |
| 运行日志 | `tmp/logs/` | 在根目录放 boot.log / raw.txt |

### app.py 拆分规则

app.py 当前 5385 行。后续大功能优先拆成独立文件：

| 模块 | 拆分条件 | 目标文件 |
|------|----------|----------|
| 自动打怪FSM | 超过1000行 | src/gui/hunt_fsm.py |
| 垂直换层 | 超过500行 | src/gui/vertical.py |
| 断线重连集成 | 逻辑独立 | src/gui/reconnect_adapter.py |
| HP/MP监控 | 逻辑独立 | src/gui/stats_monitor.py |

---

## 5. 临时文件管理

| 临时产物 | 当前散落位置 | 应统一到 |
|----------|------------|----------|
| __pycache__/ | 各目录下 | 不管，.gitignore 排除 |
| settings.json.bak_* | yolo_gui/ | tmp/backup/ |
| *.log / *.err | 散落各处 | tmp/logs/ |
| trial_log*.txt | yolo_train/ | tmp/logs/ |
| verify_out/ | yolo_train/ | tmp/verify/ |
| debug_shots/ | yolo_gui/ | tmp/debug/ |
| benchmark*.json | 根目录 | tmp/bench/ |

规则：**tmp/ 里的文件随时可删，不进版本控制，不备份**。

### 5.1 重型分析与资源清理

本节与 [`docs/ANALYSIS_WORKFLOW.md`](docs/ANALYSIS_WORKFLOW.md) 和
[`docs/ANALYSIS_RUN_CHECKLIST.md`](docs/ANALYSIS_RUN_CHECKLIST.md) 共同构成不可绕过的执行门禁。
固定顺序为：残留预检 → 输入身份锁定 → 巨型文件索引 → 受控启动 → PID/内存监控 →
`try/finally` 回收 → 临时目录删除 → 残留 PID 与清理后内存验收。任一环节缺失，任务不得标记为完成。

本节是不可绕过的执行门禁。任何一条未满足，当前分析必须停止，先完成归属审计和清理；不得以“命令很快”“文件只是读几行”或“进程应该已经退出”为理由跳过。

- 挂机工具运行时不承担 DLL、metadata、dump 或反汇编全文分析；这类工作放在逆向_纯净的离线分析流程中。
- 任何超过 100MB 的文件都禁止使用 `$lines = Get-Content 文件`、`Get-Content -Raw` 或等价整文件载入；`mxd-core-objdump.txt` 只能用流式 `rg`、`rg -A/-B` 或分块读取。
- 不为了截取几百行而先加载整份文件；巨型反汇编必须先建立地址/行号索引，再按需读取局部范围。同一轮任务不得重复整文件扫描同一个巨型文件。
- 每个分析命令都必须有超时；启动 `pwsh`、`rg`、Python、DXBC 渲染器或其他外部分析程序时记录根 PID 和子进程 PID。**必须通过 `scripts/run_scoped_analysis.ps1` 启动**，不得用无包装器的直接调用替代。
- 每次调用包装器都必须传入 `-InputPath`，让包装器流式计算输入文件身份；分析结果必须包含输入路径、字节数、`STREAM_ONLY`/`BOUNDED` 分类、修改时间和 SHA-256。没有这些字段，不得把任务标记为完成。
- 复杂子命令优先在当前 PowerShell 会话中用 `&` 调用包装器；不要让外层 `pwsh -File` 误解析子程序的 `-Command` 等短横线参数。参数必须作为独立 `-ArgumentList` 元素传入。
- 包装器必须继续监控已记录的子进程，即使根进程提前退出；根 PID 退出不等于整项任务完成。
- 每次调用必须提供可定位的 `-CommandLineNeedle` 和 `-InputPath`；包装器在参数缺失时拒绝启动。
  预检发现匹配残留 PID 时阻止本轮启动，只报告、不误杀；不得靠换标签规避预检。
- 任务开始前按本次分析文件或命令行关键字检查残留进程；只结束本轮明确创建且确认属于本轮的 PID，禁止误杀游戏、Codex、反作弊或其他用户程序。
- 正常完成、失败、超时或用户取消时，都必须通过 `try/finally` 回收本轮子进程并删除本轮临时目录；不得留下后台分析进程。
- 单个分析进程工作集达到或超过十进制 1GB（1,000,000,000 字节）时立即停止并报告 PID；不得把“内存持续增长”拖到更高阈值才处理。包装器不得使用 PowerShell 的二进制 `1GB` 字面量。
- 每次重型操作结束都要确认：本轮 PID 是否全部退出、是否仍有匹配的 `pwsh`/`rg`/Python/渲染器、临时目录是否删除、峰值内存是否恢复正常。
- 包装器收尾必须记录 `POST_CLEANUP_TRACKED_PROCESS_MEMORY_BYTES` 和
  `POST_CLEANUP_MEMORY_STATUS=RESTORED`；仅看到根进程退出，不得视为内存清理完成。
- 根进程正常退出不代表任务完成：必须继续回收本轮已经记录的子 PID，并输出 `TRACKED_PROCESS_IDS` 与 `RESIDUAL_MATCHING_PIDS`；只有 `RESIDUAL_MATCHING_PIDS=NONE` 才算清理验收通过。
- 外部分析命令的 stdout/stderr 必须写入本轮临时目录，回显只保留有限尾部行数，避免日志输出反过来占用大量内存。
- 输出排空、根进程退出等待和清理等待也必须有有限边界；不得因为等待子进程继承的输出句柄而把任务变成无界等待。输出排空超时按失败路径处理，并仍须完成 `try/finally` 清理和最终验收。
- 巨型反汇编上的 `rg -A/-B` 不是默认安全方案：如果目标模式可能高频命中、单行很长或上下文会膨胀，先停止并改用 `build_objdump_index.py`、`scan_binary_tokens.py` 或 `read_binary_windows.py`；本轮曾实测带上下文 `rg` 触发 1GB 内存保护，不能重复同类调用。
- 地址索引脚本允许追加 `--anchor`，应把本轮目标地址/唯一字节锚点一并建立到同一个轻量索引中，后续按偏移取窗口，不重复扫描巨型文件。
- 并行运行多个分析/验证任务时，为每个任务设置独立输出目录和等待边界；不得让多个任务重复扫描同一个巨型反汇编文件。
- 临时文件清理解决的是磁盘和孤立进程问题，不等同于清理游戏状态；不能把“杀进程后自动重连”当作测谎规避方案。
- 每次任务必须保留统一验收记录：`INPUT_FILE`、`INPUT_BYTES`、`INPUT_CLASS`、
  `INPUT_SHA256`、`STARTED_PID`、`TRACKED_PROCESS_IDS`、`MEMORY_LIMIT_BYTES`、
  `CLEANUP_CREATED_PROCESSES`、`CLEANUP_TEMP_DIRECTORY`、
  `POST_CLEANUP_TRACKED_PROCESS_MEMORY_BYTES`、`POST_CLEANUP_MEMORY_STATUS`、
  `RESIDUAL_MATCHING_PIDS`、`PEAK_WORKING_SET_BYTES` 和 `ANALYSIS_STATUS`。
  缺少任一字段，或清理状态不是 `COMPLETE`/`RESTORED`，都不得开始下一轮分析。

#### 5.1.1 固定执行顺序

每轮分析同时填写 [`docs/ANALYSIS_RUN_CHECKLIST.md`](docs/ANALYSIS_RUN_CHECKLIST.md)。它是本节的执行凭证，不是可选的说明文档。

1. **预检**：先按本次输入文件名或唯一任务标签查找残留命令行；只记录，不误杀不属于本轮的进程。
2. **锁定输入**：通过包装器记录绝对路径、大小、修改时间和 SHA-256；超过 100MB 的输入必须标记为 `STREAM_ONLY`。
3. **建立索引**：巨型反汇编先做一次流式地址/行号索引；局部分析只读索引命中的窗口。
4. **受控启动**：所有 `pwsh`、`rg`、Python、DXBC 渲染器和其他外部分析程序都经包装器启动，必须有超时、唯一标签和输入身份。
5. **监控**：单个进程工作集达到 `1,000,000,000` 字节立即停止，并记录 PID；不等待其继续增长。
6. **统一收尾**：正常完成、失败、超时、内存熔断和用户取消都必须进入 `try/finally`，回收已记录的根/子 PID并删除本轮临时目录。
7. **验收**：只有 `CLEANUP_CREATED_PROCESSES=COMPLETE`、`CLEANUP_TEMP_DIRECTORY=COMPLETE`、`RESIDUAL_MATCHING_PIDS=NONE` 和 `POST_CLEANUP_MEMORY_STATUS=RESTORED` 同时成立，才允许继续下一轮。

禁止事项：

- 禁止对超过 100MB 的文件使用 `$lines = Get-Content`、`Get-Content -Raw` 或等价整文件载入；尤其禁止整读 `mxd-core-objdump.txt`。
- 禁止用通配符或进程名批量结束 `pwsh`、`rg`、Python、游戏、Codex 或其他用户程序。
- 禁止在清理验收缺失、残留 PID 非 `NONE` 或清理后内存非 `RESTORED` 时启动并行分析。

### 5.2 测谎触发处理边界

- NonFinite/AntiMacro 被检测到时，安全策略是停止自动输入、暂停导航和攻击、记录状态并报警。
- 不自动移动鼠标、不模拟 RawInput、不注入 PointerEventData、不修改成功/失败状态、不伪造结果包。
- 现有 `lie_detector_killer.py` 属于历史秒杀逻辑；在代码策略完成迁移前，不得把它描述为可靠的测谎解决方案，也不得据此承诺“躲过判定”。

---

## 6. 文档规范

### 项目文档

| 文档 | 位置 | 内容 |
|------|------|------|
| README.md | 根目录 | 项目说明 + 快速开始 + 架构（唯一入口） |
| WORK_RULES.md | 根目录 | 本文件（工作规范） |
| AGENTS.md | 根目录 | 长期协作规则和局部执行边界 |
| CHANGELOG.md | docs/ | 版本历史，每次大改动追加 |
| 设计决策 | docs/decisions/ | 重要架构选择的理由 |

### 禁止

- 在根目录放 STATUS.md / benchmark.json / raw.txt / boot.log 等散文件
- 用 .bak_* 做备份（用 tmp/backup/ 或版本控制）
- 调试截图不清理

---

## 7. 代码质量

### 修改已有文件前

1. 先读文件头部了解模块职责
2. 先搜代码库里有没有类似实现
3. 改完后跑 `python -m py_compile 文件.py` 验证语法

### 新增代码

1. 先搜GitHub有没有成熟方案（规则2）
2. 先看同类模块怎么写的，保持风格一致
3. 不引入未确认的第三方库
4. 所有新函数加 docstring（中文，给普通人看的那种）

### 安全

- 不把 API key / 密码 / token 写进代码
- 不 commit 个人配置路径
- 键盘输入用 Interception 驱动，不用 pyautogui（容易被检测）

---

## 8. 禁止事项

| 禁止 | 原因 |
|------|------|
| 对需要外部方案或新分析链路的任务跳过搜索直接写代码 | 容易重复造轮子或选错方案 |
| 在逆向_纯净中写入Bot代码 | 污染逆向环境 |
| 复制逆向数据到本项目 | 数据只有一份，直接读引用 |
| 覆盖原始配置文件 | 用备份目录或版本控制 |
| 不验证就提交代码 | 跑 py_compile 检查语法 |
| 在 app.py 里无限追加代码 | 超过2000行必须拆模块 |
| 在根目录放散文件 | 统一放 docs/ 或 tmp/ |
