---
name: heartmula
description: HeartMuLa 音乐生成模型 — Suno-like 开源音乐生成，支持歌词+标签生成完整歌曲，多语言
version: 1.0.0
tags: [media, music-generation, ai-music, suno-like, audiocraft]
---

# HeartMuLa Skill

设置和运行 HeartMuLa 开源音乐生成模型（Suno-like）。

## 核心功能

- 歌词 + 标签 → 完整歌曲生成
- 多语言支持
- 全曲结构（Intro/Verse/Chorus/Bridge/Outro）

## 安装

```bash
# 克隆仓库
git clone https://github.com/heartmula/heartmula.git
cd heartmula

# 安装依赖
pip install -r requirements.txt
```

## 使用

```python
from heartmula import MusicGenerator

generator = MusicGenerator()
song = generator.generate(
    lyrics="Verse 1: ...\nChorus: ...",
    tags=["pop", "upbeat", "summer"],
    duration=180  # seconds
)
song.save("output.wav")
```
