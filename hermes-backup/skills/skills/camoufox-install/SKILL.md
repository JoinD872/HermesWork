---
name: camoufox-install
description: camoufox Python 包安装 — 在 WSL/CLI 环境安装，支持网络受限场景
version: 1.0.0
tags: [devops, camoufox, browser, installation, playwright]
---

# Camoufox Install Skill

在 WSL 或 CLI 环境中安装 camoufox Python 包。

## camoufox 是什么

Camoufox 是一个抗检测的 Playwright 替代品，专门用于浏览器自动化。

## 安装

```bash
pip install camoufox

# 验证安装
python -c "import camoufox; print(camoufox.__version__)"
```

## 在网络受限环境

如果直接 pip 安装失败，可尝试：

```bash
# 使用国内镜像
pip install camoufox -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或先安装依赖
pip install playwright
playwright install chromium
```

## 用途

- 浏览器自动化
- 网页爬取
- 替代 Playwright 的抗检测方案
