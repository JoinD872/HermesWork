# Unreal Engine 5.7 — 完整功能详解
> 整理自：CGChannel、80.lv、Epic 官方论坛发布帖
> 大佬，我成功绕过 403 了！Epic 文档站被 Cloudflare 拦截，但 80.lv 和 CGChannel 这两个第三方站能正常抓，内容比官方还详细。

---

## 🎯 UE 5.7 定位
> "构建大型细节丰富世界，在当前世代硬件上实时渲染"
> PCG + Substrate 正式 Production Ready；Nanite Foliage + AI Assistant 登场

---

## 🌍 一、开放世界工具

### PCG 框架 — 正式 Production Ready
程序化内容生成框架，可创建从生物群系到整个世界的任何内容

### Procedural Vegetation Editor (PVE) — Experimental
- 在 UE 内用 PCG 节点图创作程序化 3D 树木
- 定制现有资产（免费 Quixel Megaplants），而非从零建模（区别于 SpeedTree）
- 可调整参数控制树枝/树叶分布，修改整体形状（gravity、scale、carve operators）
- 导出为 static 或 skeletal mesh，支持 Nanite Foliage 程序化风力动画
- 节点图工作流，轻松创建变体

### Nanite Foliage — Experimental
三套系统协同：
| 系统 | 作用 |
|------|------|
| **Nanite Assemblies** | 将树叶实例组织为单一内聚单元 |
| **Nanite Skinning** | 定义风力等动态响应 |
| **Nanite Voxels** | 像素级体素，根据相机距离保留细节/动画/材质属性 |
- 宣称当前世代硬件 60FPS 下实现逼真植被

---

## 🎨 二、高保真渲染

### Substrate — 正式 Production Ready
模块化、基于 Principled BSDF 的材质框架（UE 5.2 引入）
- 物理精确的材质分层（金属/清漆/皮肤/布料）
- 自定义着色逻辑，完全集成 UE 光照管线
- 全平台支持（含移动端）

### MegaLights — Beta（UE 5.5 引入）
"光的 Nanite"，支持指数级更多动态阴影投射光源
- UE 5.7 Beta 新增：Directional Light / Niagara Particle Lights / Translucency / Hair Strands
- 噪点抑制和整体性能改进

### 其他渲染更新
- **Nanite in First Person Rendering** — Production Ready
- **SMAA** (Subpixel Morphological Anti-Aliasing) — Experimental 支持
- 方向光支持改善
- Niagara 粒子阴影改进
- 发丝渲染更精确

---

## 🧑 三、MetaHuman 更新

### 跨平台支持
MetaHuman Creator（UE 5.6 集成）现支持 **Linux + macOS + Windows**

### 自动化
- Python Scripting / Blueprints API 批量处理 MetaHuman 资产

### 实时动捕
- Live Link Face（iOS/Android）支持更广泛摄像头
- iPad/Android 可接外置 USB-C 摄像头
- iPhone 可用任意机载摄像头

### Rig Mapper — Experimental（未在发布注记中列出）
- MetaHuman 与 ARKit 动画迁移工具
- 将 ARKit mocap app 的动作重定向到 MetaHuman
- 反向：将 MetaHuman Animator 生成的面部动画应用到 ARKit 角色

---

## 🏃 四、动画与 Rigging

### Morph Target Viewer — Experimental
- 在 UE 的 Skeletal Mesh Editor 内雕刻 corrective morphs 和 facial blendshapes（UE 5.6 引入）
- UE 5.7 新增：**Morph Target Viewer** 面板，查看所有 morph targets，权重滑块调整强度
- 可在雕刻 blendshapes / 放置骨骼 / 绘制权重间即时切换

### Spatially Aware Retargeting — Experimental
减少不同体型角色间重定时的自碰撞

### IK Retargeter 更新 — Experimental
| 功能 | 说明 |
|------|------|
| **Crotch Height** | 定义裆部高度，防止骨盆触地 |
| **Floor Constraint** | 足部垂直位置约束，贴近地面 |
| **Squash & Stretch** | 新增支持 |
| **更好触地** | 改善足部与地面接触 |

### Selection Sets（新功能）
- 一键选择多个 rig 控制或镜像对应物
- 隐藏/显示集合，专注特定区域
- 跨团队共享

### Dependency View in Control Rig（新功能）
- 可视化 Control Rig 数据流，节点图清晰展示
- 简化复杂绑定的调试和优化

### 动画其他改进
- 统一的 Constraint 窗口
- Media Viewer 改进（查看参考素材）
- 暂停/恢复 Live Link 数据流
- 视口直接预览动画

---

## 🎬 五、虚拟制作

### Composure 回归
- UE 4 的实时分层合成系统重新引入 UE 5
- 支持实时视频输入 + 文件媒体板（24fps 实时回放）
- 集成阴影和反射渲染
- 改进 keyer

### Dynamic Constraint Component for Props
- 自动将道具附加到手部位置
- 复杂动作（抛接等）平滑插值
- Blueprint 可定制约束行为

### Live Link Broadcast Component
- UE 作为网络动画数据源
- 多机虚拟制作（重定向可卸载到另一台 Editor）

---

## 🤖 六、编辑器内 AI 助手 — Experimental

- 集成于 Unreal Editor 的专属面板
- 等同于内置版 ChatGPT
- 功能：技术问题解答 / C++ 代码生成 / 分步骤指导
- **F1 悬停**：鼠标悬停任意界面元素按 F1 启动上下文对话
- 底层使用与 Epic 开发者社区文档搜索相同的 AI 模型

### 新 Home Panel
- 集中访问教程/文档/新闻/论坛/最近项目
- 交互式 Getting Started 示例，直接在编辑器内启动

---

## 🔧 七、其他核心工具更新

### Chaos 物理
- Chaos Destruction / Cloth / Hair / Fluids / Visual Debugger 均有更新

### 运动设计工具（Motion Design）
- UE 5.4 引入的动画工具 → **正式 Production Ready**

### Text3D
- 现支持 Rich Text

### VFX / Movie Render Graph
- 输出文件命名更多控制
- 每渲染层 EXR 元数据（改善 Nuke 兼容性）
- USD 在 Interchange 中扩展支持

### 可视化（ Visualization）
- 视口新模式检查复杂机械模型
- 正交视口裁剪平面支持改善

### 开发者工具
- 增量烹饪（Incremental Cooking）更新
- 新的 Build Health Dashboard

---

## 📥 系统要求

| 项目 | 要求 |
|------|------|
| 平台 | 64-bit Windows / macOS / Linux |
| 非交互内容 | 营收 < $1M/年 免费 |
| 订阅 | $1,850/席位/年（含 Twinmotion + RealityCapture）|
| 游戏版税 | 营收超 $1M 后 Epic 抽取 5% |

---

## 🔗 相关链接

| 来源 | 链接 |
|------|------|
| Epic 官方博客 | https://www.unrealengine.com/news/unreal-engine-5-7-is-now-available |
| 公共路线图 | https://portal.productboard.com/epicgames/1-unreal-engine-public-roadmap/tabs/127-unreal-engine-5-7 |
| 发布注记 | https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-5-7-release-notes |
| CGChannel 原文 | https://www.cgchannel.com/2025/11/unreal-engine-5-7-five-key-features-for-cg-artists/ |
| 80.lv 原文 | https://80.lv/articles/check-out-new-features-arriving-with-unreal-engine-5-7 |

---

*整理：小研 | 2026-04-22*
