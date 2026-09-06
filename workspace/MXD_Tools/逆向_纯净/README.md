# 冒险岛怀旧服（v079）逆向数据 — 纯净环境

> 协作入口：先读上级 [`AGENTS.md`](../AGENTS.md)，再读本目录 [`AGENTS.md`](AGENTS.md)、[`WORK_RULES.md`](WORK_RULES.md) 和 [`CODEX_STATUS.md`](CODEX_STATUS.md)。

> 游戏：MapleStory Classic (冒险岛怀旧服) · Unity IL2CPP · BlackCipher反作弊
> 版本：GameAssembly.dll 122MB timestamp 0x6a880ac6 (2026-08-26) · global-metadata.dat v39 · Unity 6000.3.16f1
> 整理日期：2026-09-05
>
> 工作规范见 [WORK_RULES.md](WORK_RULES.md)（纯净边界 + GitHub优先 + 数据分级）

> 最新 NonFinite 核心分析：[`analysis/nonfinite_core_analysis_20260905.md`](analysis/nonfinite_core_analysis_20260905.md)。当前结论已修正为：Type125 的 `List<Vector4>` 经客户端变换后填充 F0；F8 是核心循环采样到的离散格点序列，采样时机仍未知，且会被序列化。F0 与 currentCell 是否在同一判定表达式中相遇仍未知，服务端校验也未知。30 是逻辑网格维度，不是已证实的 F0 列表长度。

### NonFinite 文档权威顺序

1. `analysis/nonfinite_core_analysis_20260905.md`：第一事实源。
2. `analysis/README.md` 与本 README：摘要入口。
3. `desktop/NonFinite核心算法逆向分析.md`：阅读版，不能覆盖第一事实源。
4. `02_pseudo/`、`04_packet/` 及其他旧 analysis：历史/辅助证据，必须以最新核心报告为准。

单条技术结论统一使用 `CONFIRMED / STRONG_INFERENCE / UNKNOWN`；报告总体可靠性为 `C`。

---

## 目录结构

```
逆向_纯净/
├── README.md              本文件
├── WORK_RULES.md          工作规范
├── 01_dump/               IL2CPP dump
│   ├── il2cppdump/        Il2CppDumper v39产出
│   │   ├── dump.cs        完整C#类结构（48MB, 16845类）
│   │   ├── il2cpp.h       结构体定义（120MB）
│   │   ├── script.json    方法地址/Ghidra脚本（131MB）
│   │   ├── stringliteral.json  字符串字面量（1.8MB）
│   │   └── *.dll (100+)   重建.NET程序集
│   ├── new_meta_dump.json     手动dump（16845类逐行解析）
│   ├── new_classes.json       5个关键类偏移
│   ├── new_analysis.md        漂移分析报告
│   ├── drift_report.json      漂移对比
│   └── strings_anti_macro_*.txt  反作弊字符串300条
│
├── 02_pseudo/             反作弊伪代码（6个UIAntiMacro + D4/D5）
├── 03_assets/             地图/跳跃数据（705图/21731平台/787传送门）
├── 04_packet/             网络协议（密钥/opcode/位置包）
├── 04_shader/             Shader逆向（LieDetector）
├── 05_data/               游戏数据文档
│
├── analysis/              分析报告 + 解析脚本
│   ├── static_analysis_20260831.md          第一批：JsonObject/MonoBehaviour/WZ
│   ├── static_analysis_batch2_20260831.md   第二批：ti=1532/1681/传送门/技能/Camera
│   ├── static_analysis_batch3_20260831.md   第三批：网络包/装备系统/WZJS字符串池
│   ├── static_analysis_batch4_20260831.md   第四/五批：WZJS格式/技能/NPC
│   ├── parse_wzjs.py                        WZJS字符串池解析器
│   ├── parse_wzjs_values.py                 WZJS数值编码解析器
│   ├── extract_monster_values.py            怪物属性提取器
│   └── monster_data.json                    920个怪物数据
│
└── 资源包/                游戏Bundle（2.2GB，130,145字符串）
```

---

## 已定位的游戏实体架构

```
网络层
  └── cf979349 (PacketReader, ushort opcode)
      └── ti=1533 单例管理器 (Lazy<T>)
          ├── [PacketType(N)] 属性标注 → 18个handler (Opcode 90/279-298)
          ├── Dictionary<int, ti=1532> 地图实例管理
          └── ti=1532 (MonoBehaviour, 地图实体容器)
              ├── 75字段 / 144方法 / 15个网络包handler
              ├── SortingGroup + ContactFilter2D + Rect×2 + LineRenderer×2
              ├── 10个List (实体分组)
              ├── ba8f5f70 (16参数核心更新方法)
              └── c495db3f (实体工厂)

视觉层
  └── ti=1611 (MonoBehaviour实体基类)
      ├── SortingGroup + List<NameTag> + 碰撞检测虚方法
      └── ti=1681 (NPC/怪物/其他玩家渲染器)
          ├── 44字段 / 94方法
          ├── Update RVA 0x12458E0 (可Hook)
          ├── [0x120/0x128] 外观字典×2 (ti=1686)
          │   ├── Dictionary<部位枚举(125+种), 外观条目>
          │   ├── Dictionary<模型类型(47种), 模型数据>
          │   └── Dictionary<int, List<槽绑定>>
          ├── [0x130-0x140] Sprite×3 (主体/叠加/阴影)
          └── [0x160] string 名称

渲染组件
  └── ti=1553 (acf84a97, MonoBehaviour + SpriteRenderer)
      └── 支持颜色/透明度/位置/Sprite切换，工厂方法
```

---

## 资源包数据

| Bundle | 大小 | 条目 | 字符串数 | 关键数据 |
|--------|------|------|---------|---------|
| 怪物 | 5MB | 920+ | 5,034 | level/maxHP/maxMP/PADamage/MADamage等22字段 |
| 技能 | 3.4MB | 88个 | 1,458 | mpCon/damage/mobCount/cooltime/lt/rb等 |
| NPC | 0.8MB | 950 | 1,537 | Name/Func/Talk/Quest（与ti=1013验证通过） |
| 地图 | 42.5MB | 934 | 22,966 | foothold/ladder/portal/warp |
| 角色 | 134.7MB | 8,039 | 98,315 | weapon/armor/equip/stat |
| **总计** | **~187MB** | **11,925** | **130,145** | |

### WZJS格式（已逆向）

```
MonoBehaviour对象:
[0-11]   12B header (zeros)
[12-19]  int32 version=1, type=1
[20-27]  8B hash
[28-31]  int32 ID字符串长度
[32..]   ID ASCII字符串 + null
[40-183] 索引表 (36 int32 = 144B)
[184-211] WZJS头 ("WZJS" + ver=5, count=2)
[212..N] WZJS二进制数据 (-1=字段边界, 类型标记+值)
[N..M]   字符串池 (3 int32头 + "{ID}{action}{frames}${field_names}")
[M..]    字符串表索引 (int32数组)
```

---

## character ti=1200（已确认，全部stable）

| 字段 | 类型 | 偏移 |
|------|------|------|
| actionid | String | 0x10 |
| charid | String | 0x18 |
| charlevel | Int32 | 0x20 |
| charname | String | 0x28 |
| charClass | String | 0x30 |
| fieldid | String | 0x38 |
| posxyz | 引用→(x:Double@0x10, y:Double@0x18, z:Double@0x20) | 0x80 |

## Camera方法链（全部stable）

```
Camera.get_main (RVA 81580816)
  → get_transform (RVA 82015600)
    → get_position (RVA 82124768) → Vector3(x@0, y@4, z@8)
    → get_forward (RVA 82128032)
WorldToScreenPoint (RVA 81579168)
ScreenPointToRay (RVA 81580576)
```

**2D简化公式**: `screen_x = world_x * sc + ox`, `screen_y = world_y * sc + oy`

---

## 网络包分发机制

```
网络数据 → ti=1533.b37c0b62(slot, opcode, param, packet)
  → Dictionary<int, ti=1532>.TryGetValue(opcode)
  → ti=1532.f8e110da(slot, packet)  // 35KB handler
    → packet.f2445547() ReadInt32 → 实体ID
    → packet.ac76fd65() ReadString → 名称
    → ti=1532.ba8f5f70(16参数) → 更新实体
    → ti=1532.c495db3f(string,bool,intx4,bool) → 创建实体
```

ti=1533 处理 Opcode: **90, 279-290, 292-296, 298**（共18个）

---

## 反作弊体系

- **BlackCipher**：内核级反作弊（SDGame32.sys），阻止OpenProcess/ReadProcessMemory
- **UIAntiMacro**：6个测谎UI（非有限/文字验证码/角色名/引导/公告/工具）
- **F1密钥**：格式化串加密（Format链+Concat链），头公式/IV链/版本300已逆向，密钥需动态截取
- **Shader**：LieDetectorShaderModule通过渲染管线做屏幕检测

---

## 工具指南

### Il2CppDumper v39（Windows81 fork）

```bash
Il2CppDumper.exe GameAssembly.dll global-metadata.dat [output_dir]
# 需修改 config.json: "RequireAnyKey": false
```

### WZJS解析器

```bash
python analysis/parse_wzjs.py           # 提取920个怪物字段名
python analysis/parse_wzjs_values.py    # 提取WZJS数值
python analysis/extract_monster_values.py # 提取怪物属性
```

### dnSpy / Ghidra

- 打开 `01_dump/il2cppdump/Assembly-CSharp.dll` 浏览所有类结构
- script.json 可生成Ghidra导入脚本

---

## GitHub方案（待集成）

| 工具 | 仓库 | 用途 | 状态 |
|------|------|------|------|
| frida-il2cpp-bridge | vfsfitvnm/frida-il2cpp-bridge | 运行时dump/trace/heap扫描 | 需隔离VM |
| il2cpp-frida-mcp | axhlzy/il2cpp-frida-mcp | AI辅助IL2CPP分析 | 需隔离VM |
| VRChat RE管线 | dwgx/vrchat-il2cpp-re | 哈希字段名恢复（85.1%） | 参考价值 |
| Il2CppDumper v39 | Windows81/Il2CppDumper | IL2CPP dump | ✅ 已集成 |

---

## 后续方向

### 需要隔离VM（阻塞中）

1. **Frida Hook ti=1681.Update (RVA 0x12458E0)**：追踪NPC/怪物位置
2. **Hook ti=1533.Instance**：获取Dictionary<int, ti=1532>当前地图实例
3. **F1密钥动态截取**（4-8h）：Frida Hook Format/Concat链
4. **封包解密闭环**（3-5h）：用真实key验证8B keepalive
5. **反作弊评估**（6-10h）：ScyllaHide bypass BlackCipher

### 纯静态（可立即做）

1. **WZJS数值提取**：解析器已写好，运行提取920个怪物的level/maxHP/maxMP实际值
2. **地图传送门完整图**：portal_report.json已有，可做路径规划
3. **技能伤害公式分析**：88个技能字段已提取，可分析mpCon/damage关系

---

## 已排除（非逆向内容）

- `bot/`, `yolo/`, `yolo_gui/`, `yolo_train/` — Bot代码 + YOLO训练
- `.trainenv/`, `build_env/` — Python虚拟环境
- `06_inject/` — DLL注入实验
- `P0_*/`, `P1_C/` — 反检测迭代实验
- `assets/`（逆向/assets） — 25K解包图集
- `diag/`, `templates/`, `shots/` — 调试截图
