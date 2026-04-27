---
name: huggingface-hub
description: Hugging Face Hub Python 客户端 — 下载/上传模型和数据集，管理预训练模型仓库，支持文件和元数据操作。
category: mlops/inference
---

# huggingface-hub

Hugging Face Hub Python 客户端，通过 `pip install huggingface_hub` 安装后使用。

## 核心功能

- 下载模型/数据集文件（单个文件或整个仓库）
- 上传模型到 Hub（`create_repo` / `upload_file` / `upload_folder`）
- 管理模型元数据（README metadata、tags）
- 缓存管理（默认缓存路径 ~/.cache/huggingface）
- 处理 LFS（Large File Storage）大文件

## 常用 API

```python
from huggingface_hub import hf_hub_download, snapshot_download
from huggingface_hub import create_repo, upload_file

# 下载单个文件
hf_hub_download(repo_id="meta-llama/Llama-2-7b", filename="config.json", cache_dir="./models")

# 下载整个仓库
snapshot_download(repo_id="meta-llama/Llama-2-7b", cache_dir="./models")

# 上传文件
upload_file(path_or_fileobj="./model.bin", path_in_repo="pytorch_model.bin", repo_id="user/model")
```

## CLI 工具

```bash
huggingface-cli login
huggingface-cli download user/model
huggingface-cli upload model.bin user/model/model.bin
```

## 缓存目录

默认：`~/.cache/huggingface/`
- `hub/` — 模型仓库缓存
- `datasets/` — 数据集缓存
- `tokenizer/` — 分词器缓存

## 认证

```python
from huggingface_hub import login
login(token="hf_xxxx")  # 写入 ~/.cache/huggingface/token
```

## 已知限制

- 下载大模型建议配合 `hf_transfer` 加速（需额外安装）
- 国内访问需设置镜像：`HF_ENDPOINT=https://hf-mirror.com`
