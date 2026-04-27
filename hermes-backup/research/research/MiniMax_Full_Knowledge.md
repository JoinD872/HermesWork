# MiniMax 开放平台 — 完整知识库
> 整理自：platform.minimaxi.com 文档中心（2026-04-22）
> by 小研

---

## 🏢 平台概览

MiniMax 是一家专注于人工智能的中国科技公司，自主研发覆盖**文本、语音、视频、图像、音乐**五大模态的模型。

**两大计费模式：**
- **Token Plan（订阅制）** — 固定月费，全模态模型打包
- **按量计费（Pay as you go）** — 按实际消耗付费

---

## 🤖 模型体系

### 文本模型
| 模型 | 定位 | 上下文 | 输出速度 |
|------|------|--------|---------|
| **MiniMax-M2.7** | 旗舰，开启自我迭代 | 204,800 | ~60 TPS |
| **MiniMax-M2.7-highspeed** | 同效果，速度大幅提升 | 204,800 | ~100 TPS |
| **MiniMax-M2.5** | 顶尖性能+极致性价比 | 204,800 | ~60 TPS |
| **MiniMax-M2.5-highspeed** | 同效果，速度大幅提升 | 204,800 | ~100 TPS |
| **MiniMax-M2-her** | 角色扮演/多轮对话专用 | — | — |
| **MiniMax-M2.1** | 多语言编程专家 | — | — |
| **MiniMax-M2** | 高效编码+Agent工作流 | — | — |

### 语音模型
| 模型 | 定位 |
|------|------|
| **Speech-2.8-HD** | 新一代HD，情绪渲染+语气词，极致音质 |
| **Speech-2.8-Turbo** | 新一代Turbo，极致速度，更自然 |
| **Speech-2.6-HD** | 极致音质韵律，生成更快更自然 |
| **Speech-2.6-Turbo** | 超低时延，响应灵敏 |
| **Speech-02-HD** | 出色韵律稳定性，复刻相似度高 |
| **Speech-02-Turbo** | 小语种增强 |

### 视频模型
| 模型 | 定位 |
|------|------|
| **Hailuo-2.3** | 全新，肢体/表情/物理/指令遵循全面突破 |
| **Hailuo-2.3-Fast** | 图生视频，更快更优惠 |
| **Hailuo-02** | 1080p原生，SOTA指令遵循，10s视频 |

### 图像模型
| 模型 | 定位 |
|------|------|
| **image-01** | 文生图/图生图，画面细腻 |
| **image-01-live** | 手绘/卡通等画风增强 |

### 音乐模型
| 模型 | 定位 |
|------|------|
| **Music-2.6** | 翻唱+器乐，最长5分钟 |
| **music-cover** | 参考音频一键翻唱，风格迁移 |

---

## 💰 Token Plan 定价

### 月付
| 套餐 | 价格 | M2.7 | Speech 2.8 | image-01 | 视频 |
|------|------|------|-----------|---------|------|
| **Starter** | ¥29 | 600次/5h | — | — | — |
| **Plus** | ¥49 | 1,500次/5h | 4,000字/日 | 50张/日 | — |
| **Max** | ¥119 | 4,500次/5h | 11,000字/日 | 120张/日 | 2个/日 |
| **Plus-极速版** | ¥98 | 1,500次/5h(M2.7-hs) | 9,000字/日 | 100张/日 | — |
| **Max-极速版** | ¥199 | 4,500次/5h(M2.7-hs) | 19,000字/日 | 200张/日 | 3个/日 |
| **Ultra-极速版** | ¥899 | 30,000次/5h(M2.7-hs) | 50,000字/日 | 800张/日 | 5个/日 |

### 年付（享折扣）
| 套餐 | 价格 | 节省 |
|------|------|------|
| Starter | ¥290/年 | ¥58 |
| Plus | ¥490/年 | ¥98 |
| Max | ¥1,190/年 | ¥300 |
| Plus-极速版 | ¥980/年 | ¥196 |
| Max-极速版 | ¥1,990/年 | ¥398 |
| Ultra-极速版 | ¥8,990/年 | ¥658 |

> Music-2.6：所有套餐均为100首/天限免（每首≤5分钟）

---

## ⏱️ 用量重置机制

| 模型类型 | 机制 |
|----------|------|
| **文本模型（M2.7）** | 5小时滚动窗口，超限后自动释放 |
| **非文本模型** | 每日配额，次日00:00重置 |

**查看用量：**
```bash
curl --location 'https://www.minimaxi.com/v1/token_plan/remains' \
--header 'Authorization: Bearer <API Key>'
```

---

## ⚡ 流量规则（动态限流）

**高峰期：** 工作日 15:00–17:30（动态调整）

**持续调用上限（高峰期）：**
- Starter/Plus：约1个Agent
- Max：约2个Agent
- Ultra：约4个Agent

**周额度限制：**
- 2026-03-22前购买：❌ 不受限制
- 2026-03-23起购买：每周限额 = 5h额度 × 10倍

> ⚠️ Token Plan 面向**个人开发者交互式场景**，生产环境建议用 Pay as you go

---

## 🔑 API Key 规则

| 类型 | 用途 | 与普通Key混用 |
|------|------|-------------|
| **Token Plan API Key** | 订阅制，文本按请求数，非文本按日配额 | ❌ 不可 |
| **普通 API Key** | 按量付费，消耗账户余额 | ❌ 不可 |

> 两者**完全独立**，不可混用

---

## 🔌 API 接口体系

### 文本 (Anthropic API 兼容 - 推荐)
```
Base URL: https://api.minimaxi.com/anthropic
SDK: pip install anthropic
环境变量:
  ANTHROPIC_BASE_URL=https://api.minimaxi.com/anthropic
  ANTHROPIC_API_KEY=${YOUR_API_KEY}
```

**支持参数：** model, max_tokens, stream, system, temperature, tool_choice, tools, top_p, thinking, metadata

**支持消息类型：** text, tool_use, tool_result, thinking

**不支持：** image, document, top_k, stop_sequences

### 语音合成
```
POST https://api.minimaxi.com/v1/t2a_v2
备用：https://api-bj.minimaxi.com/v1/t2a_v2
```

**核心参数：**
- `model`: speech-2.8-hd/turbo, speech-2.6-hd/turbo, speech-02-hd/turbo
- `text`: ≤10000字符，支持 `\\n` 段落和 `<#x#>` 停顿
- `voice_setting`: voice_id, speed, vol, pitch, emotion
- `audio_setting`: sample_rate, bitrate, format, channel

**语气词标签（仅2.8）：** (laughs), (chuckle), (coughs), (breath), (groans), (sighs) 等

### 视频生成
- 文生视频 / 图生视频 / 首尾帧 / 主体参考
- Agent 模式

### 图像生成
- 文生图 / 图生图

### 音乐生成
- 音乐生成 / 歌词生成

### 文件管理
- 上传 / 列出 / 检索 / 下载 / 删除

---

## 🛠️ AI 编程工具集成

**支持的工具（Token Plan）：**
| 工具 | 集成方式 |
|------|---------|
| Claude Code | MCP |
| Cursor | MCP |
| OpenCode | MCP |
| Hermes Agent | 原生接入 |
| Cline | MCP |
| Roo Code | MCP |
| Grok CLI | MCP |
| Codex CLI | MCP |
| Droid | MCP |
| Zed | MCP |
| MonkeyCode | — |
| TRAE | MCP |

**MCP 工具（Token Plan专属）：**
- `web_search` — 网络搜索
- `understand_image` — 图片理解

**MCP 安装（Claude Code）：**
```bash
claude mcp add -s user MiniMax \
  --env MINIMAX_API_KEY=api_key \
  --env MINIMAX_API_HOST=https://api.minimaxi.com \
  -- uvx minimax-coding-plan-mcp -y
```

---

## 🤖 Hermes Agent 接入

```bash
# 安装
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# 验证
hermes doctor

# 配置（选择 MiniMax China + Token Plan API Key + M2.7）
hermes model

# 启动
hermes
```

---

## 💡 M2.7 使用技巧

1. **指令明确清楚** — 说明期望的输出格式、内容、风格
2. **补充"为什么"** — 告诉模型目的，它能举一反三
3. **注重举例** — 给"样板"示例，明确指出不要犯的错
4. **长任务分段** — 利用出色的状态追踪，聚焦有限目标
5. **上下文感知** — 临近容量阈值时可能提前终止，注意控制
6. **多窗口工作流** — 分阶段处理，重启vs压缩的选择

**建议 System Prompt：**
> 这是一项非常冗长的任务，建议您充分利用完整的输出上下文来处理——整体输入和输出 tokens 控制在 200k tokens，充分利用上下文窗口长度将任务彻底完成，避免耗尽 tokens。

---

## ❓ 常见问题

### 充值方式
- 在线充值（微信）
- 对公汇款（仅企业，需实名认证一致）

### 开票
- 抬头必须与实名认证主体一致
- 个人账号无法开企业抬头发票
- 代金券抵扣部分不可开票

### 余额预警
支持，余额低于设定值时邮件/短信/站内信通知

### 声音复刻（克隆）
需完成**个人实名认证**或**企业认证**

### 退款
❌ 不支持，一经购买确认

### 升级
订阅期内随时可升，支付差价立即生效

---

## 📞 联系方式

| 类型 | 渠道 |
|------|------|
| 使用问题 | 官方客服群（二维码） |
| 开发者交流 | 飞书群（二维码） |
| 商务合作 | api@minimaxi.com |
| 开票/退款 | api@minimaxi.com |
| 技术支持 | 使用问题咨询群 |

---

## 📅 模型发布时间线

| 日期 | 模型 | 说明 |
|------|------|------|
| 2026-04 | Music-2.6 | 翻唱+器乐 |
| 2026-03-18 | M2.7 | 全新旗舰，开启自我迭代 |
| 2026-03 | Music-2.5+ | 纯音乐解锁 |
| 2026-02 | M2.5 | 编程/工具调用SOTA |
| 2026-01-23 | Speech-2.8 | 自然语气词 |
| 2026-01-16 | Music-2.5 | 全维度突破 |
| 2025-12-22 | M2.1 | 多语言编程专家 |
| 2025-10-30 | Music-2.0 | 5分钟创作 |
| 2025-10-29 | Speech-2.6 | 新一代HD |
| 2025-10-28 | Hailuo-2.3 | 物理表现全面升级 |
| 2025-10-27 | M2 | 高效编码+Agent |
| 2025-09-11 | Music-1.5 | 4分钟时长 |
| 2025-08-06 | Speech-2.5 | 更多语种 |
| 2025-06-20 | Music-1.5B | 灵感+歌词输入 |
| 2025-06-18 | Hailuo-02 | 1080P+10s视频 |
| 2025-06-16 | M1 | 推理模型，80K思维链 |
| 2025-04-02 | Image-01 | 图像生成 |
| 2025-02-11 | T2V/I2V-01-Director | 导演级视频 |
| 2025-01-15 | Text-01/VL-01 | 新一代文本+视觉 |

---

*整理：小研 | 2026-04-22*
