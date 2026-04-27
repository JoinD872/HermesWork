---
name: outlines
description: 结构化文本生成 — JSON/Pydantic/Regex 约束保证，有限状态机 token 过滤，支持 Transformers/vLLM/llama.cpp，Pydantic 模型集成
version: 1.0.0
tags: [mlops, inference, structured-generation, json, pydantic, grammar]
---

# Outlines Skill

Guarantee valid JSON/XML/code structure during generation using finite state machines.

## 核心概念

- **FSM 约束**：在 token 级别过滤无效 token，零开销
- **Pydantic 集成**：自动将 Pydantic 模型转换为 JSON Schema
- **Grammar-Based**：支持 regex、JSON Schema、上下文无关文法

## 使用示例

```python
from pydantic import BaseModel
import outlines

class User(BaseModel):
    name: str
    age: int
    email: str

model = outlines.models.transformers("microsoft/Phi-3-mini-4k-instruct")
generator = outlines.generate.json(model, User)
result = generator("Extract: John, 30, john@example.com")
```

## 支持后端

- Transformers (Hugging Face)
- vLLM
- llama.cpp
