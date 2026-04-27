---
name: manim-video
description: Manim 数学/技术动画制作流水线 — 3Blue1Brown风格，概念解释/方程推导/算法可视化/架构图/数据故事/论文解释，需要 LaTeX 环境
version: 1.0.0
tags: [creative, manim, animation, mathematics, video, education]
---

# Manim Video Production Pipeline

Manim Community Edition 制作数学/技术动画的完整流水线。

## 模式

| 模式 | 输入 | 输出 |
|------|------|------|
| Concept explainer | 主题/概念 | 动画解释 + 几何直觉 |
| Equation derivation | 数学表达式 | 分步动画证明 |
| Algorithm visualization | 算法描述 | 步进式执行可视化 |
| Data story | 数据/指标 | 动画图表/对比 |
| Architecture diagram | 系统描述 | 组件逐步构建 |
| Paper explainer | 研究论文 | 关键发现动画 |
| 3D visualization | 3D 概念 | 旋转曲面/参数曲线 |

## 技术栈

- Manim Community Edition v0.20+
- LaTeX (texlive / mactex)
- ffmpeg
- ElevenLabs / Qwen3-TTS (可选配音)

## 工作流

```
PLAN → CODE → RENDER → STITCH → AUDIO → REVIEW
```

## 输出质量

| 质量 | 分辨率 | FPS |
|------|--------|-----|
| -ql (draft) | 854x480 | 15 |
| -qm (medium) | 1280x720 | 30 |
| -qh (production) | 1920x1080 | 60 |

## 色彩风格

- **Classic 3B1B**: BG=#1C1C1C, BLUE=#58C4DD, GREEN=#83C167, YELLOW=#FFFF00
- **Warm academic**: BG=#2D2B55, 暖色调
- **Neon tech**: 深黑背景霓虹色
- **Monochrome**: 深蓝灰单色
