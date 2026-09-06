# 冒险岛怀旧服（v079）外部挂机工具

> 协作入口：先读 [`AGENTS.md`](AGENTS.md)，再读 [`WORK_RULES.md`](WORK_RULES.md)。当前状态见 [`CODEX_STATUS.md`](CODEX_STATUS.md)。

纯外部方案——屏幕采集 + YOLO识别 + 驱动级输入，不碰游戏进程。

> 测谎说明：当前 NonFinite 已确认是动态数据驱动的轨迹验证。检测到测谎后杀进程并自动重连不等于取消判定，也不是可靠的规避方式；工具文档以安全停机、报警和保留证据为准。

> 工作规范见 [WORK_RULES.md](WORK_RULES.md)

## 快速开始

```
1. 安装 Python 3.11 + pip install opencv-python numpy onnxruntime-gpu Pillow pywin32 mss
2. 双击 run.bat
3. 打开游戏，点【开始检测】→ 画面出现绿框 = 识别正常
4. 勾选【自动打怪】→ 工具自动寻怪攻击
```

F8 暂停/恢复。游戏窗口需保持在前台。

## 架构

```
屏幕采集(ScreenGrabber) → YOLO检测(Detector) → 状态决策(App) → 驱动输入(Keyboard)
         ↑                      ↑                    ↑
    小地图定位              模型热插拔           HP/MP监控
    (MinimapTracker)     (models/*.onnx)       (BarMeter)
```

核心原则：只读屏幕像素，不读游戏内存，不注入DLL，不抓包。

## 目录结构

```
挂机工具/
├── README.md                         项目说明（本文件）
├── WORK_RULES.md                     工作规范
├── run.bat                           启动入口（→ yolo_gui/app.py）
├── .gitignore                        版本控制排除规则
│
├── yolo_gui/                         主程序（GUI + 挂机逻辑）
│   ├── app.py                        主入口（5385行，含FSM状态机）
│   ├── detector.py                   YOLO检测器封装（单模型/多模型）
│   ├── screen.py                     游戏窗口定位 + mss截屏
│   ├── keyboard.py                   Interception驱动级键盘输入
│   ├── minimap.py                    小地图玩家定位（HSV金点检测）
│   ├── map_identity.py               地图身份识别（像素特征索引）
│   ├── stats_bar.py                  HP/MP血条像素监控
│   ├── platform_layer.py             平台归属层（坐标转换/跳跃校准）
│   ├── world_route.py                世界跑图（跨地图传送门导航）
│   ├── route_editor.py               路线编辑器GUI
│   ├── lie_detector_killer.py        测谎检测历史秒杀逻辑（待迁移为SAFE_STOP）
│   ├── calibrate_stats.py            血条校准工具
│   ├── check_name.py                 名字牌检测
│   ├── build_map_identity_index.py   地图索引构建
│   ├── settings.json                 运行配置（1332行）
│   ├── routes.json                   路线数据
│   ├── map_identity_index.json       地图特征索引
│   ├── reconnect/                    断线重连模块
│   │   ├── detector.py               界面状态检测（断线/登录/选服/选角）
│   │   ├── fsm.py                    可恢复状态机（16态完整流程）
│   │   └── mouse.py                  鼠标点击封装
│   └── templates/reconnect/          重连界面模板图片（10张）
│
├── yolo/                             YOLO推理引擎
│   ├── yolo_infer.py                 ONNX推理（GPU优先，cuDNN9）
│   ├── models/                       当前使用的模型
│   │   ├── user_muyao.onnx           木妖检测
│   │   └── user_player.onnx          玩家检测
│   └── cudnn_bin/                    cuDNN9运行库（8个DLL，自包含）
│
├── yolo_train/                       YOLO训练工具
│   ├── app.py                        训练GUI（标注→训练→验证）
│   ├── labeler.py                    交互式标注器
│   ├── trainer.py                    训练任务管理
│   ├── auto_label.py                 自动标注
│   ├── capture.py                    截图采集
│   ├── extract_frames.py             精灵表帧提取
│   ├── classes.json                  类别定义（295种怪物）
│   ├── data/                         训练数据集
│   ├── data_trial/                   试验数据集
│   └── frames/                       怪物帧库（302种）
│
├── configs/                          默认配置
│   └── default.json
│
├── docs/                             文档（CHANGELOG / 设计决策）
├── tmp/                              临时文件（随时可删，不进版本控制）
│   ├── logs/                         运行日志
│   ├── backup/                       配置备份
│   ├── debug/                        调试截图
│   ├── verify/                       验证输出
│   └── bench/                        基准测试数据
│
└── E:\Opencode\MXD\逆向_纯净\        逆向数据（只读引用，不在本目录内）
    ├── 03_assets/new_map.json        705张地图平台数据
    └── 03_assets/jump_calib.json     跳跃校准参数
```

## 核心模块说明

### 检测与识别

| 模块 | 职责 | 原理 |
|------|------|------|
| `detector.py` | 加载YOLO模型，返回怪物框 | onnxruntime GPU推理 |
| `minimap.py` | 定位玩家在小地图上的位置 | HSV金点检测 + G/R比例过滤 |
| `map_identity.py` | 识别当前地图ID | 小地图像素特征匹配 |
| `stats_bar.py` | 读取HP/MP百分比 | 多行扫描填充终点中位数 |
| `check_name.py` | 检测怪物名字牌 | 模板匹配 |

### 自动打怪FSM

```
SEARCH(找怪) → CHASE(追怪) → ATTACK(攻击) → LOOT(拾取) → SEARCH...
                  ↓
            TRAVERSE(垂直换层：跳台/爬绳/掉落)
```

状态机运行在30Hz，关键参数：
- `attack_range`：攻击距离阈值
- `kill_confirm`：击杀确认帧数
- `patrol_delay`：巡逻延迟
- `wall_escape_s`：卡墙超时

### 断线重连

16态完整流程：
```
IN_GAME → DISCONNECT → CLICK_OK → WAIT_LOGIN → CLICK_CONNECT
→ WAIT_WORLD → WORLD_SELECT → WAIT_CHAR → CHAR_SELECT
→ WAIT_GAME → GAME_READY → RESET → RESUME
```

支持自然断线后的状态恢复。测谎触发后的“杀进程→自动重连”不应作为规避流程；相关行为需经过安全策略审查。

### 跑图系统

- `world_route.py`：跨地图传送门导航（APPROACH→PORTAL→WAIT_LOAD→VERIFY）
- `platform_layer.py`：平台归属判定（坐标→世界坐标→小地图坐标转换）
- `route_editor.py`：GUI路线编辑器（Canvas预览玩家/传送门/到达点）

### 垂直换层：单绳诊断

换层排查时先不要使用自动换层：

1. 先点击“开始检测”，等待状态显示“检测中”。不要先勾选“自动打怪”。
2. 在“单绳诊断”下拉框选择要测试的那一根绳。
3. 点击“检查这根”，确认地图、人物和入口距离都有结果。
4. 保持“演练”开启时点击“执行这根”，只会记录流程而不会发游戏按键；演练会一直占用测试状态，完成查看后点击“停止测试”。演练期间不会启动自动打怪。
5. 需要真实执行时，必须先通过安全验收，再关闭“演练”；测试结果会写入 `hunt_debug.log`。

每次启动 `run.bat` 会自动清空上一轮的 `hunt_debug.log`；同一次运行中切换自动打怪不会清空诊断记录。

“执行这根”始终使用下拉框选中的 edge，不会再根据人物位置自动改测另一根绳。

### 安全机制

| 机制 | 说明 |
|------|------|
| 测谎处理 | 目标策略：检测到 AntiMacro 后进入 SAFE_STOP、停止自动输入并报警；旧 `taskkill` 逻辑不代表能跳过判定 |
| 热键暂停 | F8 暂停/恢复所有自动操作 |
| 卡键释放 | 启动时自动松开残留按键 |
| 看门狗 | 检测结果超时自动停止移动 |

## 配置

主要配置在 `yolo_gui/settings.json`，关键字段：

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `conf` | 检测置信度阈值 | 0.6 |
| `attack_key` | 攻击按键 | A |
| `jump_key` | 跳跃按键 | D |
| `auto_hunt.enabled` | 自动打怪开关 | false |
| `auto_hunt.attack_range` | 攻击距离 | 20px |
| `auto_hunt.kill_confirm` | 击杀确认帧数 | 3 |
| `model` | 当前模型路径 | user_player.onnx |
| `reconnect.enabled` | 断线重连 | true |

模型热插拔：将 `.onnx` 放入 `yolo/models/`，重启程序即可。

## 依赖

### Python 3.11

```
opencv-python
numpy
onnxruntime-gpu    # GPU推理
Pillow
pywin32            # 窗口操作
mss                # 屏幕截图
```

### 硬件

- NVIDIA GPU（CUDA 12.x + cuDNN 9，已内置于 `yolo/cudnn_bin/`）
- Interception驱动（`keyboard.py` 需要，用于驱动级输入）

### 逆向数据（可选，跑图功能需要）

跑图/平台归属功能依赖逆向分析产出的地图数据，从 `E:\Opencode\MXD\逆向_纯净\03_assets\` 只读引用：
- `new_map.json`：705张地图平台数据
- `jump_calib.json`：跳跃校准参数

NonFinite 的静态审查报告位于 `E:\Opencode\MXD\逆向_纯净\analysis\nonfinite_core_analysis_20260905.md`，仅作为离线研究资料，不是挂机工具的自动答题模块。

要查看与录屏外观对应的离线小游戏复刻（默认是游戏场景内嵌画面），请进入 `挂机工具` 后运行：
`python offline_nonfinite\nonfinite_visual_clone.py`。如果只检查 768×600 Prefab 逻辑窗口，显式加
`--prefab-window`。旧的
`nonfinite_practice_clone.py` 现在默认转到该视觉入口；只有显式加
`--grid-practice` 才会打开历史网格诊断窗口。

## 版本历史

当前版本：1.79

- v1.79：下跳验证 + 中文动作 + 垂直换层v2
- v1.78：垂直换层（下跳+爬绳+掉落）
- v1.77：目标锁定WEAK绑定 + MOVE_STUCK诊断
- v1.76：ATTACK_RETAIN换怪优化
- v1.75：身份链修复（track_id统一）
