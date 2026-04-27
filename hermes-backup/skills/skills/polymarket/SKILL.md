---
name: polymarket
description: Polymarket 预测市场数据查询 — 搜索市场/获取价格/订单簿/价格历史，只读无需 API key
version: 1.0.0
tags: [research, polymarket, prediction-market, markets, api]
---

# Polymarket Skill

通过公开 REST API 查询 Polymarket 预测市场数据。

## 核心功能

- 搜索预测市场
- 获取市场价格
- 订单簿数据
- 价格历史
- 市场元数据

## 使用

无需 API key，只读接口：

```bash
# 获取市场信息
curl "https://clob.polymarket.com/markets?active=true"

# 获取价格
curl "https://clob.polymarket.com/prices?market=0x..."

# 订单簿
curl "https://clob.polymarket.com/orderbook?market=0x..."
```

## 用途

- 预测市场数据查询
- 决策参考
- 市场情绪分析
