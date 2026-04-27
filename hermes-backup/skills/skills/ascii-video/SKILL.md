---
name: ascii-video
description: ASCII 艺术视频制作流水线 — 视频→ASCII转换/音频反应式可视化/生成式动画/混合音视频/文字歌词叠加/实时终端渲染，MP4/GIF/图像序列
version: 1.0.0
tags: [creative, ascii, video, animation, creative-coding]
---

# ASCII Video Production Pipeline

将视频、音频、图片转换为彩色 ASCII 字符艺术视频输出（MP4、GIF、图像序列）。

## 模式

| 模式 | 输入 | 输出 |
|------|------|------|
| Video-to-ASCII | 视频文件 | ASCII 再现 |
| Audio-reactive | 音频文件 | 音频驱动生成可视化 |
| Generative | 无 | 程序生成 ASCII 动画 |
| Hybrid | 视频+音频 | ASCII视频+音频反应叠加 |
| Lyrics/text | 音频+文本 | 计时文字+视觉效果 |

## 技术栈

- Python 3.10+, NumPy, SciPy
- Pillow (图像处理)
- ffmpeg (视频编解码)
- OpenCV (可选，视频帧采样)
- ElevenLabs API (可选，TTS 配音)

## 输出格式

- MP4 (H.264)
- GIF (640x360 @ 15fps)
- PNG 序列

## 质量标准

- 首帧即完美不过修
- 每帧内容饱满，不过黑背景
- 跨场景统一美学语言
