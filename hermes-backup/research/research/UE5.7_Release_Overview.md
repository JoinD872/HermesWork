# Unreal Engine 5.7 — Release Overview
> 来源：Epic Developer Community Forums（发布帖）| 日期：2025年11月12日
> 原文：[UE 5.7 Released](https://forums.unrealengine.com/t/unreal-engine-5-7-released/2673913)

---

## 📌 核心定位
UE 5.7 提供**在大规模开放世界上构建细节丰富世界的工具**，在当前世代硬件上实现实时渲染。
三大方向：程序化生成大规模环境、物理精确材质、更多动态光源（改进性能）。

---

## 🌍 一、开放世界工具（Open World Tools）

### PCG 框架 — Production Ready
- **PCG Editor Mode**：新的专用编辑器模式，提供可定制工具库
  - Draw Spline（样条线绘制）
  - Paint / Create Volume（画笔 / 体积创建）
  - 每工具绑定一个 PCG Graph，实时控制，无需代码
- **GPU 计算提速**：参数覆盖（Parameter overrides）支持 GPU 节点
- **Polygon2D 数据类型 & 操作符**：支持闭合区域处理
- **新样条线操作符**
- **Procedural Vegetation Editor (PVE)**：展示 PCG 灵活性
  - 在 UE 内创建和定制植被资产生成 Nanite Skeletal Assemblies
  - **Experimental 首版支持 Quixel Megaplants**（目前在 Fab 免费下载，5个物种，支持尺寸和结构变化）

### Nanite Foliage（Experimental）
- 使用 **Nanite Voxels** 渲染密集细节环境
- 绘制数百万微小重叠元素，形成实体高细节表面（树冠、地面杂物）
- 无需 LOD，无 popping
- 使用 **Nanite Assemblies** 减少存储/内存/渲染成本
- **Nanite Skinning**：支持风响应等动态效果
- 支持 PVE 生成的网格，可通过 USD 从外部工具导入树木

---

## 🎨 二、高保真渲染（High-Fidelity Rendering）

### Substrate — Production Ready
- 模块化材质系统，**物理精确的材质分层**（金属/清漆/皮肤/布料等）
- 可实现多层车漆、油皮等逼真效果
- 自定义着色逻辑，完全集成 UE 光照管线
- 全平台支持（含移动端）

### MegaLights — Beta
- 支持**更多动态阴影投射光源**
- 复杂面积光源的逼真软阴影
- 改善整体视觉保真度
  - 更好的 directional lights 支持
  - Translucency 改进
  - Niagara 粒子阴影
  - 更精确的发丝渲染
  - 开箱即用的性能和噪点抑制增强，减少手动光源优化

---

## 🧑 三、MetaHuman 集成

| 功能 | 详情 |
|------|------|
| **跨平台插件** | MetaHuman Creator UE 插件现已支持 **Linux 和 macOS** |
| **自动化处理** | 支持 Python / Blueprint 批量处理 MetaHuman 资产 |
| **Mesh Conforming** | 支持多变姿势下带 UV 空间顶点对应的网格conform，DCC 往返（FBX） |
| **实时动捕** | 通过 Live Link Face 支持 iPad / Android 设备实时表演捕捉 |
| **发丝编辑** | 在 UE 内用关节形变/画笔/网格操控创作和控制发丝和发股，模拟物理与动画间混合 |
| **Houdini 更新** | 新的引导驱动工作流，预设发型可选 |

---

## 🏃 四、动画与绑定（Animation & Rigging）

### 动画模式重构（Refactored Animation Mode）
- 精简工作流，优化屏幕空间

### Selection Sets（新功能）
- 一键选择多个绑定控制或镜像对应物
- 隐藏/显示集合便于专注
- 跨团队共享

### IK Retargeter 改进
- 更好的足部触地
- 支持 squash & stretch 动画
- 空间感知防止自碰撞
- 不同体型角色间准确触地点维持

### Skeletal Editor 更新
- 添加行业标准雕刻工作流
- 骨位放置/权重绘制/blend shape 雕刻无缝切换
- 即时更新，数十个 blend shape 的绑定创建更快

### 其他
- **单向物理世界碰撞**：角色与环境自然交互，更逼真的布娃娃和游戏测试
- **依赖视图（Dependency View）**：可视化 Control Rig 数据流，节点图清晰展示，简化调试和优化

---

## 🎬 五、虚拟制作（Virtual Production）

### Dynamic Constraint Component for Props
- 自动将道具附加到手部位置
- 复杂动作（如抛接）也能平滑插值
- Blueprint 可定制约束行为

### Live Link Broadcast Component
- UE 作为网络动画数据源
- 支持多机虚拟制作设置（如将重定向卸载到另一台 Editor）

### Composure 实时合成工具更新
- 更易用、功能更强
- 支持实时视频输入和文件媒体板（24fps 实时回放）
- 集成阴影和反射渲染，混合实拍与 CG
- 改进 keyer 更高质量抠像

---

## 🤖 六、编辑器内 AI 助手 & 新 Home Panel

| 功能 | 说明 |
|------|------|
| **AI 助手面板** | 实时引导，可答问题、生成 C++ 代码、分步骤帮助 |
| **F1 悬停** | 鼠标悬停任意界面元素按 F1 启动关于该功能的上下文对话 |
| **Home Panel** | 集中访问教程/文档/新闻/论坛/最近项目 |
| **Getting Started** | 新用户提供交互式入门示例，直接在编辑器内启动 |

---

## ⚠️ 其他重要说明

- **Linux SDL2 → SDL3**：UE 5.7 起 Linux 从 SDL2 迁移到 SDL3，有 SDL2 定制需适配
- **Windows ARM64 / ARM64EC 支持**（Experimental）
  - ARM64ec 支持完整源码构建，但不支持 Launcher editor
  - ARM64 打包（via Launcher）高度实验性

---

## 🔧 已知问题修复（5.7.1 ~ 5.7.4）

累计修复 **200+** issue，涵盖：
- PCG 崩溃/内存问题
- Nanite / Lumen / Path Tracing 崩溃
- MetaHuman 毛发/布料崩溃
- nDisplay 故障
- iOS/Android 打包问题
- 动画重定向/Retargeter 问题
- Composure 合成问题
- WebBrowser 崩溃
- 等等……

---

## 📥 下载链接
- [Epic Games Launcher](https://www.unrealengine.com/en-US/download)
- [GitHub](https://github.com/EpicGames)
- [Linux](https://www.unrealengine.com/linux)

---

*报告整理：小研 | 2026-04-22*
