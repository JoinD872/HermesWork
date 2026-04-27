---
name: dspy
description: Stanford DSPy 声明式 AI 编程 — 自动优化 Prompt，模块化 RAG 系统，22k+ GitHub stars，Signatures/Modules/Optimizers
version: 1.0.0
tags: [mlops, research, dspy, prompt-engineering, rag, stanford]
---

# DSPy Skill

DSPy = Declarative Language Model Programming，Stanford NLP 出品的 AI 系统编程框架。

## 核心概念

### Signatures（签名）
定义输入输出结构：
```python
class QA(dspy.Signature):
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")
```

### Modules
- `dspy.Predict` — 基础预测
- `dspy.ChainOfThought` — 思维链推理
- `dspy.ReAct` — Agent-like reasoning with tools
- `dspy.ProgramOfThought` — 代码生成推理

### Optimizers
- `BootstrapFewShot` — 从示例学习
- `MIPRO` — Prompt 迭代优化
- `BootstrapFinetune` — 生成微调数据集

## 使用

```python
import dspy
lm = dspy.Claude(model="claude-sonnet-4-5-20250929")
dspy.settings.configure(lm=lm)

qa = dspy.Predict("question -> answer")
result = qa(question="What is the capital of France?")
```
