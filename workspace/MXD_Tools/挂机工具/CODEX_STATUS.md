# MXD_Tools 架构收口状态

## 当前协作规则（2026-09-06）

- 统一规则见上级 `AGENTS.md`；挂机工具局部规则见本目录 `AGENTS.md` 和 `WORK_RULES.md`。
- 工作角色固定为：用户定义效果，GPT 分析和提出方案，Codex 检查并实现，GitHub 保存代码版本，测试/日志/实机提供行为证据。
- 完成状态固定为：`实现完成 → 验证通过 → 用户验收`。
- 验证证据必须绑定同一个提交号、运行环境/配置、证据类型和实际结果。
- 如果提交后又有未提交修改，不能把新版本的测试或运行结果算给旧提交。
- 每个任务必须有明确的本轮目标、允许修改、禁止修改、验收标准和验证方式；流程按风险选择，不机械要求所有任务走同一套步骤。

## Phase 13：当前 NonFinite 构建与复刻口径（2026-09-06）

- 当前审计对象已切换为安装目录中的新构建：`GameAssembly.dll` SHA-256 为
  `09FBCB26665A93D4E71D5052828069C29CDAA884A44C282EE2A79E66FCE84329`，
  `global-metadata.dat` SHA-256 为
  `E58608AFD0517DD724A723429C6D07440D98A6CE0F5BBA24D898375E3D07EA1D`。
- 当前静态审计已进一步确认 Type125 → F0、PointerEventData → F8、F8 writer
  和部分 D0/材质参数链，但真实运行时参数、属性映射、服务端结果校验和最终
  SUCCESS/FAIL 闭环仍未知。
- `nonfinite_current_fidelity_retraction_20260906.md` 是当前复刻口径的权威纠正：
  默认不自动启动 DXBC harness，不使用未经证实的手写正弦/mesh 扰动，不再使用
  70%/90%/95% 作为游戏内复刻完成度。
- `nonfinite_90_replica_acceptance_20260906.md` 和
  `nonfinite_95_replica_acceptance_20260906.md` 是历史阶段记录；不能覆盖当前
  纠正，也不能单独证明线上题目画面或终态。
- 当前能诚实交付的是离线资源核对、显式 DXBC harness、录屏参考回放、F0/F8
  数据记录和回归测试；所有线上闭环结论继续标记为未知。

## Phase 11：文档与分析工作流收口（2026-09-05）

- NonFinite 最新静态结论已归档到 `逆向_纯净/analysis/nonfinite_core_analysis_20260905.md`。
- F8 记录当前量化后的离散指针轨迹；F0 按 index 读取，当前更像参考点/控制数据；目标答案列表仍未证实。
- 大型 dump、JSON 和反汇编文件统一采用搜索定位、分段读取和有限输出，禁止全文载入内存。
- 重型分析后必须检查进程树和内存占用；只清理本轮明确创建的孤立分析进程，不结束游戏或反作弊进程。
- 大文件分析与进程清理严格执行 `docs/ANALYSIS_WORKFLOW.md`：超过 100MB 的输入只允许流式/分块读取，所有外部分析命令必须经 `scripts/run_scoped_analysis.ps1`，并以 `CLEANUP_CREATED_PROCESSES=COMPLETE`、`CLEANUP_TEMP_DIRECTORY=COMPLETE`、`RESIDUAL_MATCHING_PIDS=NONE`、`POST_CLEANUP_MEMORY_STATUS=RESTORED` 作为继续工作的硬门槛。
- 包装器现在强制要求 `-InputPath` 与 `-CommandLineNeedle`；预检发现同锚点残留进程时阻止重复启动并输出 `STOPPED_PREFLIGHT_RESIDUAL`，必须先完成归属审计和定向清理。
- AntiMacro 触发后的工具策略文档统一以 SAFE_STOP、停止自动输入、报警和保留证据为准；不把杀进程重连描述为规避方案。

## Phase 6

- MapIdentity 使用 canonical 平台几何特征；live/reference 共用特征定义。
- `UNKNOWN / CANDIDATE / CONFIRMED / MISMATCH` 状态闭环。
- 只有完整 `ContextCandidate` 才能提交 `CurrentMapContext`。
- `CONFIGURED` 仅保留给显式 preview/development 查询，生产确认接口 fail-closed。
- `context_epoch` 只在新上下文 commit 时递增；invalidate 只清空当前上下文。

## Phase 7

- `ActionToken`、`NavigationLease`、`ActionProtocol` 已形成统一身份校验链。
- `MoveExecutor` 提供坐标、平台、超时、无进展和取消保护。
- `PathExecutor` 将 walk/rope/ladder/jump/drop/portal 分派给对应执行器。
- Graph `MoveExecutor` 是唯一移动物理输出；旧 movement maintainer 在 Graph
  路径活跃时完全跳过，避免重复发送和 stale 输出绕过 token。
- 旧 TRAVERSE/WorldRoute/TargetNav 的迁移期输出在 Gateway 前重新验证 Lease、
  token、session generation 与 context epoch。

## Phase 8

- `NavigationSupervisor` 维护唯一 active navigation lease，并按 WorldRoute > Target > Graph Patrol > Legacy 优先级切换。
- `GraphPatrolPlanner` 只选择 reachable 且低访问优先的平台，不发送输入。
- 低优先级请求返回 `None`，不会借用高优先级 owner 的 Lease；同一 owner 才复用
  当前 Lease，高优先级请求才会取消旧 owner。
- Graph Patrol planner 按 context epoch 持久化，路径成功/失败会记录 visit/failure。

## Phase 9

- 输入驱动组装已移到唯一 `input_bootstrap.py` 边界。
- architecture baseline 已清零并切换 strict 模式。
- STOP/PAUSE/SAFE_STOP/reconnect 的控制平面会取消全部导航运行态，
  不会让旧 World/TRAVERSE/Graph/Target 动作回落到 legacy 输入路径。

## Phase 10

- 增加六页 UI V2 只读控制平面面板：总览、挂机、导航、安全、工具、设置。
- 页面只消费状态快照；输入测试仍受 ActionPolicy 和人工接管状态保护。
- 导航状态快照补充真实 `path_state`，PathExecutor 最终成功会提交不可变
  `SUCCESS` 到 Lease。
- `ActionProtocol.dispatch()` 将 context epoch、Lease、ActionToken 校验与
  Gateway 物理提交置于同一授权锁区间，消除 commit/cancel 与发键之间的 TOCTOU。
- MapIdentity 增加低频实机诊断日志，记录状态、Top1/Top2 距离、确认进度、
  观测平台线数量及 X/Y 直方图，用于定位真实画面未确认的具体原因。
- 实时预览线程增加只读 MapIdentity heartbeat/probe；不开挂机、不启动导航时，
  也会每秒采样当前游戏画面并更新诊断，不产生任何物理输入。
- MapIdentity 增加配置地图安全否决门：视觉 Top1 与配置地图不一致时进入
  `MISMATCH`，禁止错误 `CONFIRMED` 和 CurrentMapContext 提交；确认地图变化时
  也不再黏住旧确认结果。
- 旧状态栏和 UI V2 的地图身份状态已提供中文显示，并显示配置/识别地图名称。

## 验证

- 历史阶段验收：115 项全量 unit tests、compileall、architecture scanner
  均通过；architecture baseline 为 `current=0, baseline=0, delta=0, strict`。
- 2026-09-06 当前 NonFinite 口径纠正后的视觉测试：24 项通过；这只证明离线
  入口和安全边界回归，不证明真实题目画面或线上终态。
- 旧阶段的 118 项 MapIdentity 验收仍然只适用于离线历史截图和视觉验真，真实
  Graph Patrol 与 TRAVERSE 实机验收继续暂停。
- MapIdentity 使用 `platform_struct_v3` 共享特征空间，并增加基于仓库真实
  `map_identity_index.json` 的固定 fixture 验证。
- Phase 0 稳定验收点：`62aa7a4`。
- Final Atomic Closure 代码提交 SHA：`24e4e599c31c48b6950847124babd4d8fa31dce0`。
- MapIdentity 实机诊断提交 SHA：`e66f8e2b747540b07a0d85e629d84d17791b0831`。
- MapIdentity 只读探针提交 SHA：`935d1ee5e7a2e53bfda0faf1ac89de4a416f2b5b`。
- MapIdentity 安全确认与中文状态提交 SHA：`115b4d78261110577829e1d2432c163f7e4d8b63`。
- MapIdentity V3 结构指纹代码与索引提交 SHA：`284a10d66d874f8ca7d83ba71e067c77bafaa4f1`。

## 已知 backlog

- 旧 UI 控件保留用于兼容，后续可逐步迁移到 V2 页面。
- 现有 TRAVERSE FSM 仍作为垂直动作适配器，但 Graph Callback、TargetNav、
  WorldRoute 的物理输出均经过统一 ActionProtocol/Gateway 边界；后续可继续
  将 FSM 内部状态机拆成独立 `TraverseExecutor`，不影响当前安全契约。

## MapIdentity V3 实机结论

- 新版静止实机观测 34 次：`obs_lines` 为 79～95，中位数 80，原先的
  `79 -> 28` 裁剪反馈环已消失。
- 但视觉 Top1 仍主要误判为 `107000300`，正确地图 `101030402` 未进入前五；
  原因是 V2 只比较 X/Y 各 5 桶直方图，结构区分度不足。
- V3 保留旧直方图作辅助，新增 8x8 line-mass occupancy、平台长度分布、
  Y 层结构、每层水平覆盖；线段先按 Y 层合并，降低 Hough 碎片影响。
- 配置地图仍只作为安全 veto，不参与特征加分或确认。
- 当前应继续暂停 Graph Patrol 与真实 TRAVERSE 实机验收，先重新运行
  `101030402` 的静止 20 帧测试，要求 Top1 一致率至少 90%。

## MapIdentity 在线/离线对账诊断

- V3 实机输入已经稳定，但稳定 Top1 为 `104020000`，`101030402` 仍未进前五；
  因此不再继续盲目增加 V4 特征或调阈值。
- MapIdentity 现在保留最近一次提取的原始 ROI、canvas、Canny、Hough 原始线和
  合并线诊断材料；预览探针会低频写入 `tmp/map_identity_debug/`。
- `map_identity_debug.json` 会对配置地图、Top1、Top2 输出
  `line_mass_grid`、`platform_span_hist`、Y 层、每层覆盖和旧直方图的逐块距离，
  同时记录 ROI/canvas 坐标、尺寸、canvas 来源、原始 Hough 数和合并平台数。
- 诊断只读，不参与 MapIdentity 排名、确认或任何输入动作；下一步依据一帧对账
  结果决定修 canvas、重建参考语义，还是采用“配置地图视觉验真”。
- 首次对账已经显示 `canvas_source=unconfigured`，且 ROI 与 canvas 均为
  `132x136`；目标地图的主要误差集中在 `level_x_coverage` 和 `y_level_hist`，
  说明应先确认实际 canvas 裁剪语义，不应直接继续加权重。
- 首次五张图因 Windows 中文路径的 `cv2.imwrite` 兼容问题未落盘，已改用
  `imencode + tofile` 写入；下一次采样应能得到完整图像材料。
- 已增加独立 canvas bootstrap：未确认地图时按客户端 `132/120` 画布比例
  排除捕获 ROI 底部 margin，来源标记为 `capture_aspect_fit`；它不读取地图
  ID，不参与身份评分或确认，确认后仍使用正式 WZJS canvas 元数据。

## MapIdentity 视觉验真切换

- 最新实机诊断确认 Hough 水平线对应的是美术纹理，不等价于可站立 foothold；
  Hough V3 保留为诊断/离线索引用途，不再作为生产地图确认依据。
- 生产 App 改为 `visual_reference`：配置地图只选择待验证的 PNG 参考图，
  不参与评分；比较前屏蔽黄色玩家、绿色 NPC、蓝色 Portal 和红色玩家标记，
  允许小幅画布偏移。
- 视觉比较连续 3 帧通过才提交 `CONFIRMED`；不匹配立即 `MISMATCH`，
  缺少参考图/画布/比较结果为 `UNAVAILABLE`，均不会提交地图上下文。
- 平台区域增加“保存视觉基准”按钮，参考文件位于
  `yolo_gui/map_identity_references/<map_id>.png`；目录 README 说明了采集要求。
- 本轮本地验收：118 项 unit tests、compileall、architecture strict 均通过；
  architecture baseline 为 `current=0, baseline=0, delta=0`。

## Phase 12：MapIdentity visual_reference 20 帧验收（2026-09-05）

- 使用 `yolo_train/data/images/` 中按时间连续的 20 张历史游戏全屏截图，
  按当前生产画布 `x=13..144, y=103..222` 裁剪并与
  `map_identity_references/101030402.png` 对账。
- 20/20 帧的 `visual_reference_distance` 均低于生产阈值 `0.18`；最小值
  `0.046966`，最大值 `0.100191`，平均值 `0.061463`。
- `MapIdentity` 使用 `confirm_need=3` 时，第 3 帧进入
  `CONFIRMED / 101030402`，第 4～20 帧持续保持确认。
- 该项完成的是离线历史截图稳定性验收，不等价于不同分辨率、窗口位置或
  新地图的实时实机验收；真实 Graph Patrol 与 TRAVERSE 实机验收仍保持暂停。
- 相关报告已归档至 GitHub：
  `docs/reverse-analysis/逆向_纯净/analysis/map_identity_visual_reference_audit_20260905.md`。
