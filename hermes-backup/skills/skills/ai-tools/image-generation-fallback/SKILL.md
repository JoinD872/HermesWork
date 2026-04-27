---
name: image-generation-fallback
description: 图片生成失败排查与 pollinations.ai 备用方案 — 当 MiniMax/MMX 图片生成静默失败时的替代路径
version: 1.0.0
tags: [image-generation, mmx, fallback, debug]
category: ai-tools
---

# 图片生成：MMX 失败时的 pollinations.ai 备用方案

## 已知失败模式

### MMX CLI `mmx image generate` 静默失败
- **症状**：HTTP 200 返回，但 `error.code: 6, message: "Network request failed"`
- **原因**：VPS 出口 IP（洛杉矶）访问 MiniMax API 存在网络/路由问题
- **特点**：工具报告 200 OK，但结果是错误 JSON，不是真正的网络连接失败
- **不能用**：重试多次结果相同，不是临时抖动

### MMX CLI 图片生成失败诊断流程（2026-04-26 实测）

**第一步：确认是哪个域名的问题**
```bash
# 检查两个可能的目标域名
nslookup image.minimaxi.com 8.8.8.8
nslookup image.minimaxi.com 1.1.1.1
nslookup api.minimaxi.com 8.8.8.8
```

**第二步：用 --verbose 确认 MMX CLI 实际调用的端点**
```bash
mmx image generate "test" --verbose
# 观察输出中的 > POST https://... 
# 重要：MMX CLI 图片生成用的是 api.minimaxi.com/v1/image_generation（与文本同域名）
# 不是 image.minimaxi.com！
```

**第三步：区分错误类型**
| 错误 | 含义 |
|------|------|
| `code: 6, "Network request failed"` | API 服务端不可用（不是域名 DNS 问题） |
| HTTP 530 + "Origin DNS error" | 目标域名 DNS 解析失败 |
| curl 超时无响应 | 网络层不通 |

**2026-04-26 排查结论**：
- `image.minimaxi.com` — DNS 全局 NXDOMAIN（所有 resolver 都解析不了）
- `api.minimaxi.com` — 文本 API 正常，图片 API 返回 code 6
- MMX CLI region="cn" 时使用 `api.minimaxi.com`，图片端点为 `/v1/image_generation`
- **Cloudflare Worker 代理方案失败**：Worker 内部也报 Origin DNS error，因为 image.minimaxi.com 本身 DNS 就坏了
- 结论：图片生成 API 服务端（api.minimaxi.com/v1/image_generation）不可用，任何绕过方案都无效

**调试命令备忘**：
```bash
# MMX CLI verbose 模式（必须用！能看到实际请求的 URL 和返回）
mmx image generate "test" --verbose

# nslookup 多 resolver 交叉验证
nslookup image.minimaxi.com 8.8.8.8
nslookup image.minimaxi.com 1.1.1.1
nslookup image.minimaxi.com  # 使用系统默认 resolver

# 尝试 global region（国际版）
mmx config set region global
mmx image generate "test"
mmx config set region cn  # 恢复
```

## 备用方案：pollinations.ai

**完全免费，无需 API key，直接 URL 生成**

### 基础 URL 格式
```
https://image.pollinations.ai/prompt/<URL编码的提示词>?width=512&height=512&model=flux
```

### 参数说明
| 参数 | 说明 |
|------|------|
| `width/height` | 尺寸，默认正方形 |
| `model` | 可选 `flux`（默认）或 `turbo` |
| prompt | **必须 URL 编码**，空格用 `%20` 或 `+` |

### 生成 + 下载完整流程
```bash
# 1. 生成并下载到文件
curl -fsSL --connect-timeout 30 \
  "https://image.pollinations.ai/prompt/$(python3 -c 'import urllib.parse; print(urllib.parse.quote(input()))')" \
  -o /tmp/avatar.png

# 2. 验证文件（file 命令判断类型）
file /tmp/avatar.png

# 3. 用 mmx vision describe 快速预览效果（图片理解）
mmx vision describe /tmp/avatar.png
```

## 与 MMX 的分工

| 场景 | 工具 | 原因 |
|------|------|------|
| 正常网络环境下 | `mmx image generate` | 质量更高 |
| VPS / 网络受限环境 | `pollinations.ai` | 无需 auth，直连 |
| 需要快速测试 prompt | `pollinations.ai` | 快，无配额限制 |

## 注意事项

- pollinations.ai 返回的是 **JPEG**（即使扩展名是 .png），用 `file` 命令会显示 `JPEG image data`
- 超时时间建议设 60s（默认 30s 可能不够，模型推理需要时间）
- V3/flux 模型生成较慢，建议 `--connect-timeout 60` 以上
- `mmx vision describe` 纯图片理解，默认超时 30s 可能不够，建议 60s

### pollinations.ai Rate Limiting（重要！）

**2026-04-26 实测发现：**
- 限额：`Queue full for IP: <your_ip>: 1 requests already queued (max: 1)`
- 每个 IP 只能有 1 个请求在队列里，不能并发
- 被限流时返回 **JSON**（不是图片），包含 `{"error": "Too Many Requests", ...}`
- 验证方法：`file <输出文件>`，如果输出是 JSON 就是被限流了

**应对策略：**
```bash
# 两次请求之间至少等 30 秒
sleep 30
curl -fsSL --max-time 120 "https://image.pollinations.ai/prompt/..." -o output.png
file output.png  # 确认是图片而非 JSON
```

**连续被限流时的处理：**
```bash
# 等 60 秒再试
sleep 60
curl -fsSL --max-time 120 "..." -o output.png
# 如果还是 JSON，继续等 + 重试
```

---

## 实用流程：批量生成头像候选

```bash
# 并行生成多个变体（注意：不能同时发两个请求，会被限流）
# 正确做法：串行生成，每两个之间等 30 秒

curl -fsSL --connect-timeout 60 \
  "https://image.pollinations.ai/prompt/<URL编码提示词>" \
  -o /path/to/avatar_v1.png

sleep 30

curl -fsSL --connect-timeout 60 \
  "https://image.pollinations.ai/prompt/<URL编码提示词>" \
  -o /path/to/avatar_v2.png

# 批量描述（逐个做，mmx 有超时问题）
mmx vision describe /path/to/avatar_v1.png --timeout 60
mmx vision describe /path/to/avatar_v2.png --timeout 60
```

保存路径建议：`~/.hermes/assets/avatars/`

---

## 头像定制标准工作流（实测有效，2026-04-26）

**适用场景：** 用户有明确图片需求（头像/配图），需要多轮精修才能定稿。

### 第一步：确认需求
- 问清楚用途、风格偏好、参考图（用户发图用 `mmx vision describe` 描述）
- 给出 3-5 个中文草案选项（不同动物/风格组合）
- **用户确认方向后再生成，不反悔**

### 第二步：出中文草案
格式：
```
**① 动物名**
> 中文描述段落，包含：外形特征 + 配色 + 背景元素 + 风格关键词
```
- 一次出 3-5 个选项，附调整方向说明
- 用户选出一个，或者给反馈（不喜欢哪个元素、想换什么）

### 第三步：英文 prompt 生成
用户确认中文草案后，翻译成英文 prompt，用 pollinations.ai 生成。

**翻译要点：**
- 中文偏意象（"冷酷黑客"、"数据梦境"）→ 英文要具体可执行（"cold blue feather sheen", "digital fragments floating"）
- 用逗号分隔的词组 > 完整句子（更稳定）
- 技术/数码词汇用英文（circuit/LED/data stream/glowing）
- 用户要求"不要太浓烈" → `muted`, `subtle`, `soft`, `low saturation`
- 用户要求"酷一点" → `cool and detached`, `slight smirk`
- 用户要求"可爱" → `kawaii`, `cute friendly expression`, `happy smile`

### 第四步：多轮精修
- 每次只改 1-2 个明确要素
- 每生成一次 **至少等 30 秒**（防限流）
- 验证用 `file output.png` 确认是图片而非 JSON
- 用户发截图标注红框区域 → 用 `mmx vision describe` 识别区域内容 → 针对性改 prompt

**实测有效关键词对照表：**
| 用户反馈 | prompt 调整 |
|---------|-----------|
| 太亮 | `muted`, `low saturation`, `soft muted lighting` |
| 太暗/主体不突出 | `lighter tone`, `contrasting against dark background` |
| 背景太浓烈 | `soft pale gradient background`, `muted ethereal glow`, `no harsh edges` |
| 翅膀/某个元素要去掉 | `no wings`, `wings folded closed`, 明确说不要什么 |
| 表情可爱 | `kawaii`, `cute friendly`, `happy smile` |
| 表情酷 | `cool and detached`, `slight smirk`, `cold` |
| 融合感差 | `character and background blending naturally together` |
| 角度不对 | `front-facing pose`, `looking at viewer`, `three-quarter view` |
| 颜色太深 | `slate-blue and dark grey feathers`（比 pure black 浅） |

### 第五步：定稿存档
```bash
cp /path/to/final_v6.png ~/.hermes/assets/avatars/old_v_final.png
```
建议存档路径：`~/.hermes/assets/avatars/`

---

**验证命令备忘：**
