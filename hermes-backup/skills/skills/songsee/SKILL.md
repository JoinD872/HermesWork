---
name: songsee
description: 音频频谱可视化 — 生成 mel/chroma/MFCC/tempogram 等频谱图，用于音频分析/音乐制作调试/视觉文档
version: 1.0.0
tags: [media, audio, spectrogram, visualization, music]
---

# Songsee Skill

生成音频频谱特征可视化图（mel spectrogram、chroma、MFCC、tempogram 等）。

## 核心功能

- Mel spectrogram — 梅尔频谱图
- Chroma — 色度特征
- MFCC — 梅尔频率倒谱系数
- Tempogram — 节拍特征

## 使用

```bash
# 命令行
songsee input.wav --type mel --output mel.png
songsee input.wav --type chroma --output chroma.png

# Python
from songsee import Spectrogram
spec = Spectrogram("input.wav")
spec.plot_mel("output.png")
```

## 用途

- 音频分析
- 音乐制作调试
- 可视化文档
