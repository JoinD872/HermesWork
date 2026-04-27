---
name: xurl
description: X/Twitter 操作 — 通过 xurl（官方 X API CLI）发帖/回复/引用/搜索/时间线/提及/点赞/转推/书签/DM/媒体上传/v2 原始端点访问
version: 1.0.0
tags: [social-media, twitter, x, api, post, social]
---

# X/Twitter Skill

通过 xurl 官方 X API CLI 管理 X/Twitter 账号所有操作。

## 核心功能

- **发帖/回复**：发布推文、回复、转引
- **搜索**：搜索推文和用户
- **时间线**：读取用户/关注时间线
- **互动**：点赞、转推、书签
- **DM**：发送私信
- **媒体**：上传图片/视频
- **账户**：关注/取关、用户信息

## 使用

```bash
# 发帖
xurl tweet "Hello world"

# 搜索
xurl search "from:elonmusk"

# 点赞
xurl like TWEET_ID

# 上传媒体
xurl media upload image.jpg
```

## 认证

需要 X API Bearer Token。
