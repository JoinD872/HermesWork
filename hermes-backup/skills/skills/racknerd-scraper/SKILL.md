---
name: racknerd-scraper
description: RackNerd 促销产品页完整配置信息爬取 — 正确爬取客户系统促销页，避免信息残缺
version: 1.0.0
tags: [research, racknerd, vps, scraper, hosting]
---

# RackNerd Scraper Skill

正确爬取 RackNerd 促销产品页的完整配置信息，避免信息残缺。

## 目标 URL

- 客户系统促销页：my.racknerd.com（不是 racknerd.com）
- 公开宣传页

## 爬取内容

- VPS 配置（CPU/内存/硬盘/流量）
- 价格（原价/促销价）
- 库存状态
- 位置/数据中心
- 操作系统选项

## 使用

当用户需要 RackNerd 促销产品信息时触发，直接爬取页面提取完整配置。

## 注意

目标地址是 my.racknerd.com，爬取公开页面可能获取的信息不完整。
