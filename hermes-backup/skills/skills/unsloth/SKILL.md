---
name: unsloth
description: Unsloth 加速微调 — 2-5x训练加速，50-80%内存节省，LoRA/QLoRA优化，支持 Llama/Mistral/Gemma/Qwen
version: 1.0.0
tags: [mlops, training, fine-tuning, unsloth, lora, qlora, optimization]
---

# Unsloth Skill

Unsloth 是一个加速 LLM 微调的库，比 HuggingFace 训练快 2-5 倍。

## 核心优势

- 训练速度提升 2-5x
- 内存占用减少 50-80%
- 自动优化 LoRA/QLoRA 配置
- 兼容 HuggingFace Transformers 和 TRL

## 支持模型

- Llama (所有版本)
- Mistral
- Gemma
- Qwen
- Phi

## 使用

```bash
pip install unsloth
pip install unsloth[ Ampere ]  # NVIDIA Ampere + Turing
```

```python
from unsloth import FastLanguageModel
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/llama-3.1-8b-bnb-4bit",
    max_seq_length = 2048,
    load_in_4bit = True,
)
```
