# 深度学习知识库

> 小V的深度学习核心知识储备，持续更新

---

## 一、神经网络基础

### 1.1 神经元（Neuron）

人工神经元模仿生物神经元机制：

```
输入(x₁, x₂, ..., xₙ) → 加权求和(Σwᵢxᵢ + b) → 激活函数f(·) → 输出y
```

数学表达式：
```
y = f(Σᵢ wᵢxᵢ + b) = f(w·x + b)
```

- **w**: 权重（weight），决定输入信号的重要性
- **b**: 偏置（bias），调整输出 baseline
- **f**: 激活函数，引入非线性

### 1.2 感知器（Perceptron）

最早的人工神经网络模型（Frank Rosenblatt, 1957），是一种**线性二分类器**。

**局限**：只能解决线性可分问题，**无法解决XOR问题**。

```
XOR真值表：
x₁  x₂  XOR
 0   0   0
 0   1   1
 1   0   1
 1   1   0   ← 无法用一条直线分开
```

### 1.3 多层感知器（MLP, Multi-Layer Perceptron）

解决XOR问题：加入**隐藏层**，形成多层网络。

```
输入层 → 隐藏层₁ → 隐藏层₂ → ... → 隐藏层ₙ → 输出层
```

**前向传播（Forward Propagation）**：
- 数据从输入层流向输出层
- 每层：z = Wx + b, a = f(z)
- 同一层通常使用相同激活函数

**反向传播（Backpropagation）**：
- 计算损失函数对每个参数的梯度
- 链式法则：∂L/∂w = ∂L/∂a · ∂a/∂z · ∂z/∂w
- 从输出层向输入层反向传播误差

### 1.4 激活函数（Activation Function）

激活函数引入**非线性**，让网络能学习复杂模式。

| 激活函数 | 公式 | 特点 | 适用场景 |
|---------|------|------|---------|
| Sigmoid | σ(x) = 1/(1+e⁻ˣ) | 输出(0,1)，易饱和 | 二分类输出层 |
| Tanh | tanh(x) | 输出(-1,1)，零中心 | 隐藏层 |
| ReLU | max(0,x) | 简单高效，不会饱和 | 隐藏层（默认） |
| Leaky ReLU | max(0.01x, x) | 避免Dying ReLU | 隐藏层 |
| Softmax | eˣᵢ/Σeˣʲ | 输出和为1，多分类 | 多分类输出层 |

**ReLU 的问题**：
- Dying ReLU：负值区域梯度为0，神经元死亡
- 解决：Leaky ReLU / PReLU / ELU

---

## 二、卷积神经网络（CNN）

### 2.1 为什么需要CNN？

全连接网络参数太多（图像1000×1000像素 = 10⁶维输入）。CNN通过**权重共享**大幅减少参数量。

### 2.2 核心操作

**卷积层（Convolutional Layer）**：
- 用**卷积核（kernel/filter）**在图像上滑动
- 卷积核与感受野逐元素相乘后求和
- 输出称为**特征图（feature map）**
- 参数：kernel size, stride, padding

**池化层（Pooling）**：
- 最大池化（Max Pooling）：取最大值
- 平均池化（Average Pooling）：取平均值
- 作用：降低尺寸，减少计算量，提取主要特征

**全连接层（FC Layer）**：
- 将特征图展平，进行分类/回归

### 2.3 经典CNN架构

```
LeNet (1998)    → 5层，MNIST手写识别
AlexNet (2012)  → 8层，ReLU + Dropout，ImageNet突破
VGGNet (2014)   → 16/19层，统一用3×3卷积
ResNet (2015)   → 残差连接，解决梯度消失，可达152层
EfficientNet    → 复合缩放（深度/宽度/分辨率）
```

### 2.4 ResNet 残差连接

核心思想：让网络学习残差 F(x) = H(x) - x，而不是直接学习 H(x)。

```
输入 x
  ↓
卷积层 → 卷积层 → (+) ← 输出
              ↑
输入 x ────→ (+)  ← 恒等连接（shortcut）
```

好处：梯度可以从shortcut直接传回输入，缓解梯度消失。

---

## 三、循环神经网络（RNN）与序列模型

### 3.1 RNN基本结构

```
x₁ → [RNN Cell] → h₁
x₂ → [RNN Cell] → h₂  (h₁作为记忆传入)
x₃ → [RNN Cell] → h₃  (h₂作为记忆传入)
...
```

问题：**长期依赖问题（Long-Term Dependencies）**
- 梯度在时间步反向传播时会指数级衰减或爆炸

### 3.2 LSTM（Long Short-Term Memory）

通过**门控机制**解决长期依赖：

```
遗忘门 f = σ(W_f · [h_{t-1}, x_t] + b_f)    → 决定丢弃什么信息
输入门 i = σ(W_i · [h_{t-1}, x_t] + b_i)    → 决定更新什么
候选值 C̃ = tanh(W_C · [h_{t-1}, x_t] + b_C) → 新的候选记忆
输出门 o = σ(W_o · [h_{t-1}, x_t] + b_o)    → 决定输出什么

记忆单元更新：
C_t = f * C_{t-1} + i * C̃    (选择性遗忘 + 选择性添加)
h_t = o * tanh(C_t)
```

### 3.3 GRU（Gated Recurrent Unit）

LSTM的简化版，只有两个门：

```
更新门 z = σ(W_z · [h_{t-1}, x_t])
重置门 r = σ(W_r · [h_{t-1}, x_t])

候选隐藏状态：h̃ = tanh(W · [r * h_{t-1}, x_t])

最终隐藏状态：h_t = (1-z) * h_{t-1} + z * h̃
```

### 3.4 序列到序列（Seq2Seq）

```
编码器(Encoder)     解码器(Decoder)
RNN/RNN/LSTM  →   RNN/LSTM  → 输出序列
    h_n ─────────→ 初始状态
```

应用：机器翻译、文本摘要、对话生成

---

## 四、注意力机制与Transformer

### 4.1 为什么需要注意力机制？

Seq2Seq的瓶颈：所有信息压缩到一个固定向量 h_n。注意力机制让解码器**动态选择**关注编码器哪些部分。

### 4.2 自注意力（Self-Attention）

核心公式：**Attention(Q, K, V) = softmax(QK^T / √d_k) · V**

```
Query (Q): 我当前要查询的内容
Key (K):   我有什么可以用来匹配的特征
Value (V): 实际要提取的信息
```

步骤：
1. Q与K做点积 → 相似度分数
2. 除以√d_k（缩放，防止梯度消失）
3. softmax归一化 → 注意力权重
4. 用权重对V加权求和 → 输出

### 4.3 Transformer 架构

```
                    Multi-Head Self-Attention
Input → Embedding → Positional Encoding → [Encoder] × N
                                              ↓
Output ← Linear → Softmax ← [Decoder] × N ← Encoder Output
                ↑
          Masked Self-Attention
          (防止看到未来信息)
```

**核心组件**：
- Multi-Head Attention：多个注意力头，捕获不同子空间关系
- Feed Forward Network：两层全连接 + ReLU
- Residual Connection：残差连接 + LayerNorm
- Positional Encoding：位置编码（因为self-attention不建模位置）

### 4.4 BERT vs GPT

| 模型 | 架构 | 预训练任务 | 典型应用 |
|------|------|-----------|---------|
| BERT | Transformer Encoder | MLM + NSP | 文本分类、NER、问答 |
| GPT | Transformer Decoder | 语言模型 | 文本生成、对话 |
| GPT-3/4 | 更大GPT | 语言模型 | Few-shot学习 |

---

## 五、优化算法

### 5.1 梯度下降（Gradient Descent）

参数更新：θ = θ - α · ∇L(θ)

- **批量梯度下降（BGD）**：整个数据集，计算慢但稳定
- **随机梯度下降（SGD）**：单个样本，快但震荡
- **小批量梯度下降（Mini-batch GD）**：两者平衡（常用）

### 5.2 动量（Momentum）

加速收敛，减少震荡：

```
v_t = βv_{t-1} + (1-β)∇L(θ)
θ = θ - α·v_t
```

物理意义：类似球的惯性，累积速度方向。

### 5.3 Adam（Adaptive Moment Estimation）

结合动量 + RMSProp，是最常用的优化器：

```
m_t = β₁m_{t-1} + (1-β₁)∇L   (一阶矩/动量)
v_t = β₂v_{t-1} + (1-β₂)∇L² (二阶矩/RMSProp)

m̂ = m_t / (1-β₁^t)   (偏差校正)
v̂ = v_t / (1-β₂^t)   (偏差校正)

θ = θ - α · m̂ / (√v̂ + ε)
```

默认参数：β₁=0.9, β₂=0.999, ε=10⁻⁸

### 5.4 学习率调度

| 方法 | 策略 |
|------|------|
| Step Decay | 每N个epoch降低学习率 |
| Cosine Annealing | 余弦曲线衰减 |
| Warmup | 初期逐渐增大学习率 |
| ReduceLROnPlateau | 监控指标不下降时降低 |

---

## 六、正则化与防止过拟合

### 6.1 过拟合（Overfitting）

模型在训练集表现好，测试集表现差。

### 6.2 正则化方法

**L1/L2正则化**：
- L2: 在损失函数加 λ||w||²（权重衰减）
- L1: 加 λ||w||₁（产生稀疏权重）

**Dropout**：
- 训练时随机丢弃一定比例神经元
- 相当于训练多个子网络，推理时使用全部

**Early Stopping**：
- 监控验证集loss，不再下降时停止训练

**Data Augmentation**：
- 图像：翻转、旋转、裁剪、颜色抖动
- 文本：同义词替换、回译

**Batch Normalization**：
- 每一层输入做标准化：均值0，方差1
- 允许更深网络训练，加速收敛

### 6.3 归一化方法对比

| 方法 | 标准化对象 | 作用 |
|------|-----------|------|
| BatchNorm | batch内特征 | 加速训练 |
| LayerNorm | 单个样本所有特征 | RNN/Transformer |
| InstanceNorm | 单个样本单个通道 | 风格迁移 |
| GroupNorm | 通道分组 | Batch小的场景 |

---

## 七、损失函数

### 7.1 分类任务

| 任务 | 损失函数 |
|------|---------|
| 二分类 | Binary Cross-Entropy: -[y·log(p) + (1-y)·log(1-p)] |
| 多分类 | Categorical Cross-Entropy |
| 多标签 | Binary Cross-Entropy per label |

### 7.2 回归任务

| 任务 | 损失函数 |
|------|---------|
| 标准回归 | MSE (Mean Squared Error) |
| 鲁棒回归 | MAE (Mean Absolute Error) |
| 两者结合 | Huber Loss |

### 7.3 特殊任务

| 任务 | 损失函数 |
|------|---------|
| 对比学习 | Triplet Loss, Contrastive Loss |
| GAN | 对抗损失 (Generator + Discriminator) |
| 检测/分割 | Focal Loss, IoU Loss |

---

## 八、模型评估指标

### 8.1 分类指标

```
准确率 (Accuracy) = 正确预测数 / 总数

精确率 (Precision) = TP / (TP + FP)  → 预测为正的中真正的比例
召回率 (Recall) = TP / (TP + FN)      → 真正的中被预测出的比例
F1 = 2 × (Precision × Recall) / (Precision + Recall)

AUC-ROC = ROC曲线下面积，越大越好
```

**混淆矩阵**：
```
                预测
              正   负
真实 正      TP  FN
     负      FP  TN
```

### 8.2 回归指标

```
MAE = Σ|y_i - ŷ_i| / n
MSE = Σ(y_i - ŷ_i)² / n
RMSE = √MSE
R² = 1 - SS_res / SS_tot
```

---

## 九、实践技巧

### 9.1 训练技巧

1. **权重初始化**：
   - ReLU网络：He Initialization (W ~ N(0, √(2/nₗ)))
   - Sigmoid/Tanh：Xavier Initialization

2. **梯度检查**：
   - 数值梯度 ≈ 分析梯度（误差< 10⁻⁷）

3. **学习率选择**：
   - 从 1e-3 开始，Adam默认通常work
   - 监控loss曲线判断是否合适

### 9.2 Debug清单

```
□ 训练loss下降吗？ → 否：学习率太大/太小、梯度问题
□ 验证集loss同步下降？ → 否：过拟合，需要正则化
□ 梯度消失/爆炸？ → 检查梯度尺度，加BatchNorm/残差
□ 预测结果全同？ → 学习率问题，初始化问题
□ 内存溢出？ → 减少batch size，加gradient accumulation
```

### 9.3 超参数调优

| 超参数 | 建议范围 |
|--------|---------|
| 学习率 | 1e-4 ~ 1e-2 (Adam) |
| Batch Size | 16, 32, 64, 128, 256 |
| Dropout | 0.1 ~ 0.5 |
| 隐藏层单元数 | 64 ~ 1024 |
| 层数 | 1 ~ 20 |

---

## 十、经典问题与解答

**Q: 为什么ReLU比Sigmoid好？**
A: Sigmoid梯度在(0,1)区间，层数深时梯度相乘会指数级衰减（梯度消失）。ReLU负半轴梯度为0，正半轴梯度为1，不会指数衰减。

**Q: 为什么需要残差连接？**
A: 深网络训练困难，残差让梯度直接回传，理论上网络深度不影响训练（可训练1000+层）。

**Q: Transformer vs RNN/LSTM的优劣？**
A: Transformer并行度高（无序列依赖），长距离建模能力强（O(1) attention），但O(n²)内存。RNN适合序列生成，内存高效。

**Q: BatchNorm和LayerNorm的区别？**
A: BatchNorm跨batch标准化，适合CNN和大batch；LayerNorm在样本内标准化，适合RNN和Transformer。

---

## 待深入学习
- [ ] 生成对抗网络（GAN / Stable Diffusion）
- [ ] 变分自编码器（VAE）
- [ ] 扩散模型（Diffusion Model）
- [ ] 强化学习基础（DQN / PPO）
- [ ] 联邦学习
- [ ] 模型量化与部署
