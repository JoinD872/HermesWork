---
name: weights-and-biases
description: ML 实验追踪平台 — 自动记录指标/实时可视化/Sweep 超参搜索/模型注册表/版本管理，200k+ 用户
version: 1.0.0
tags: [mlops, evaluation, experiment-tracking, wandb, hyperparameters]
---

# Weights & Biases Skill

ML 实验追踪、模型版本管理、超参优化的协作平台。

## 核心功能

- **自动指标记录**：训练 loss、准确率等自动上传
- **实时可视化**：Web Dashboard 实时查看训练曲线
- **Sweep 超参搜索**：bayes / grid / random 策略
- **模型注册表**：版本化模型、Artifact 追踪
- **团队协作**：共享项目、评论、对比实验

## 使用

```python
import wandb
wandb.init(project="my-project", config={
    "learning_rate": 0.001,
    "epochs": 10,
    "batch_size": 32
})

for epoch in range(10):
    wandb.log({"loss": train_loss, "accuracy": train_acc})
wandb.finish()
```

## 集成

PyTorch / TensorFlow / HuggingFace Transformers / PyTorch Lightning
