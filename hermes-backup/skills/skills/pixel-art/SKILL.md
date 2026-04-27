---
name: pixel-art
description: 图片转复古像素艺术 — NES/Game Boy/PICO-8/C64 硬件精确调色板，可动画为 MP4/GIF（雨/萤火虫/雪景等12种场景）
version: 2.0.0
tags: [creative, pixel-art, retro, arcade, gameboy, nes, animation]
---

# Pixel Art Skill

将任意图片转换为复古像素艺术，可进一步动画为短视频或 GIF。

## 调色板（28种）

| 预设 | 时代 | 调色板 | 像素块 |
|------|------|--------|--------|
| arcade | 80s | 自适应16色 | 8px |
| snes | 16-bit | 自适应32色 | 4px |
| nes | 8-bit | NES硬件54色 | 8px |
| gameboy | DMG | 4色绿 | 8px |
| pico8 | Fantasy Console | 16固定色 | 6px |
| c64 | Commodore 64 | 16固定色 | 8px |
| cyberpunk | 现代霓虹 | 10霓虹色 | 6px |

## 动画场景（12种）

night / dusk / tavern / indoor / urban / nature / magic / storm / underwater / fire / snow / desert

## 流程

1. 提升对比度/色彩/锐化（小调色板更强）
2. 降采样（NEAREST，无插值）
3. Floyd-Steinberg 抖动量化
4. 放大回原尺寸
5. 可选：叠加粒子动画 → ffmpeg 编码

## 使用

```python
from pixel_art import pixel_art
pixel_art("in.jpg", "out.png", preset="nes")

from pixel_art_video import pixel_art_video
pixel_art_video("out.png", "out.mp4", scene="night", duration=6)
```
