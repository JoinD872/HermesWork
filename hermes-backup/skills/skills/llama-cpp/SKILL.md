---
name: llama-cpp
description: 本地 LLM 推理框架 — CPU/Apple Silicon/AMD/Intel GPU/NVIDIA 多硬件，支持 GGUF 量化(2-8bit K-quants)，CLI/Python/OpenAI兼容服务器/Ollama/LM Studio
version: 1.0.0
tags: [mlops, inference, llm, local, cpu, gpu, quantization, gguf]
---

# llama.cpp Skill

用 llama.cpp 在各类硬件上运行 LLM 推理，支持 GGUF 量化格式。

## 支持硬件

- CPU（x86_64 / ARM64）
- Apple Silicon（Metal 加速）
- AMD GPU（ROCm）
- Intel GPU（SYCL）
- NVIDIA GPU（CUDA）

## 量化格式

| 格式 | 内存 | 质量 | 适用场景 |
|------|------|------|----------|
| Q2_K | ~3.5GB | 中等 | 极致内存受限 |
| Q3_K_M | ~4.0GB | 中等+ | 内存受限 |
| Q4_K_M | ~5.0GB | 高 | 平衡之选 |
| Q5_K_M | ~6.0GB | 很高 | 高质量需求 |
| Q6_K | ~7.0GB | 极高 | 质量优先 |
| Q8_0 | ~9.0GB | 接近FP16 | 无内存压力 |

## 使用方式

```bash
# 安装
pip install llama-cpp-python

# Python 使用
from llama_cpp import Llama
model = Llama("./model.Q4_K_M.gguf")
response = model("The capital of France is")
```

## 注意事项

2G 内存 VPS 只能跑 2B 以下小模型，7B 模型需要 8GB+ 内存。
