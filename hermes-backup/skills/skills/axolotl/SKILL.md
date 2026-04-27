---
name: axolotl
description: LLM 微调框架 — LoRA/QLoRA/DPO/KTO/ORPO/GRPO，100+模型配置，FSDP多卡，DeepSpeed，多模态支持
version: 1.0.0
tags: [mlops, training, fine-tuning, lora, qlora, dpo, axolotl]
---

# Axolotl Skill

Axolotl 是一个 LLM 微调框架，通过 YAML 配置管理训练流程。

## 支持方法

- LoRA / QLoRA
- DPO (Direct Preference Optimization)
- KTO (K-TO)
- ORPO (Odds Ratio Preference Optimization)
- GRPO (Group Relative Policy Optimization)
- SFT (Supervised Fine-Tuning)
- FSDP (Fully Sharded Data Parallel)

## 支持模型

100+ 预置配置：Llama/Mistral/Gemma/Qwen/Phi 等

## 典型配置

```yaml
base_model: meta-llama/Llama-3.1-8B-Instruct
model_type: LlamaForCausalLM
load_in_4bit: true
adapter: qlora
lora_r: 64
lora_alpha: 128
lora_dropout: 0.05
datasets:
  - path: data/training_set
    type: alpaca
```

## 使用

```bash
pip install axolotl
axolotl train config.yml
```
