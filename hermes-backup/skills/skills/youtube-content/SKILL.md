---
name: youtube-content
description: YouTube 内容提取 — 获取视频字幕并转换为结构化内容（章节/摘要/文章/线程），用户给 URL 后直接抓全部内容
version: 1.0.0
tags: [media, youtube, transcript, video, content-extraction]
---

# YouTube Content Skill

提取 YouTube 视频字幕并转换为结构化内容。

## 触发条件

- 用户分享 YouTube URL 或视频链接
- 请求总结视频内容
- 请求字幕文本
- 提取并重新格式化视频内容

## 核心功能

- 获取 YouTube 视频字幕/ transcript
- 转换为章节划分
- 生成摘要
- 转换为文章格式
- 转换为线程/推文格式

## 使用

当用户提供 YouTube URL 时自动触发，直接抓取完整内容整理给用户。

## 提取方法（按优先级）

### 方法 1：`youtube_transcript_api`（首选）
```python
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
transcript = api.fetch('<video_id>', languages=['zh-CN', 'zh-Hans', 'en'])
for item in transcript:
    print(f"{item['start']:.0f}s - {item['text']}")
```

### 方法 2：`yt-dlp`
```bash
yt-dlp --write-auto-sub --sub-lang zh-Hans,en --skip-download <url>
```

### 方法 3：Bilibili 同款视频（如果有搬运）
搜索视频标题 + "bilibili" 找搬运版本，browser 打开后抓内容

### 方法 4：搜索完整文字版
用 SearXNG 搜索 `"视频标题" 文字版/全文/整理`

## 已知障碍

### VPS IP 被 YouTube 屏蔽
**症状**：`RequestBlocked` 或 bot 验证墙
**原因**：VPS 出口 IP（洛杉矶 HostPapa）被 YouTube 封锁，云服务商 IP 基本都被屏蔽
**解决**：无法从 VPS 绕过，需要用户手动复制字幕，或换用国内设备

### Bot 验证墙
**症状**：YouTube 页面显示 "Sign in to confirm you're not a bot"
**解决**：同上，用户手动操作

### 没有字幕
**症状**：`NoTranscriptFound`
**解决**：搜索是否有博客/文章整理了同款视频内容
