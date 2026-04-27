---
name: youtube-content-extraction
description: YouTube 内容提取 — 字幕提取各方式对比、已知限制、VPS IP 被封的替代方案
tags: [youtube, transcript, video, media]
category: media
---

# YouTube 内容提取方案

## 触发条件
用户分享 YouTube URL 要求分析内容时触发。

## 字幕提取方式对比

| 方式 | 成功率 | 限制 |
|------|--------|------|
| `mmx vision describe`（截图） | ✅ 几乎100% | 只能分析画面文字，不能提取视频口述内容 |
| `youtube_transcript_api` | ⚠️ 看 IP | 云服务商 VPS IP 会被 YouTube 封锁，返回 RequestBlocked |
| `yt-dlp --write-auto-sub` | ⚠️ 看视频 | 需要视频有字幕；可能触发 Bot 验证 |
| browser 打开视频页 | ❌ 通常失败 | YouTube 有 Bot 检测，未登录被拦截 |
| SearXNG 搜索字幕文字版 | ❌ 成功率低 | 很少有人发布完整字幕 |

## 推荐流程

1. **先用 `mmx vision describe`** 对视频截图 → 获取标题/频道/描述/章节
2. **字幕提取** → 优先 `youtube_transcript_api`，被封则跳过
3. **VPS IP 被封时**：
   - 让用户在本地/手机打开视频，把字幕文本复制过来
   - 或用手机截字幕图，MMX CLI 分析
4. **都没有** → 用视频标题在搜索引擎找相关博客文章

## 已知问题

- VPS 出口 IP（192.3.241.244/RackNerd 洛杉矶）被 YouTube 部分封锁，`youtube_transcript_api` 返回 RequestBlocked
- 国内网络用户可正常使用 `youtube_transcript_api`
- Bilibili 有时会搬运 YouTube 视频字幕，可尝试搜索但成功率低

## 能分析 vs 不能分析

| 能分析 | 不能分析 |
|--------|---------|
| 视频标题、频道信息 | 视频画面中的图表 |
| 视频描述文字 | 视频里出现的代码 |
| 自动字幕内容 | 人物面部/场景 |
| 章节标题 | 音频质量/背景音乐 |
| 评论区文字 | |
