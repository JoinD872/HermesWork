---
name: research-workflow
description: 系统化搜索与深度研究规范 — 问题分类/搜索入口优先级/研究流程/停止标准
---

# Research Workflow — 系统化搜索与深度研究规范

> 来源：基于小H确认的研究实战经验总结，2026-04-24
> 适用：所有需要搜索、对比、深度研究的技术/产品类问题

---

## 核心原则

1. **问题分类决定搜索深度**，不是所有问题都用同一套力度
2. **第一手来源 > 搜索摘要**，能进页面的就进去抓完整内容
3. **外国技术社区是重要答案来源**，尤其是技术问题/产品选型/用户反馈
4. **有停止标准**，防止无限搜索

---

## 一、问题分类

| 类型 | 判断标准 | 搜索深度 | 最多工具数 |
|------|---------|---------|-----------|
| 快速事实类 | 有明确答案（版本号、日期、价格） | 浅，1次搜索+抓页面 | 2 |
| 技术实现类 | 怎么做（蓝图/代码/配置） | 中，多轮搜索 | 5 |
| 产品选型类 | 哪个好（X vs Y） | 中深，评测+反馈+benchmark | 5 |
| 深度研究类 | 完整认知（行业/趋势/全面对比） | 深，全网覆盖+多次迭代 | 8+ |
| 用户反馈类 | 真实体验（缺点/优点/问题） | 中深，第一手社区讨论 | 5 |

---

## 二、搜索入口优先级

### 通用优先级（按顺序）

```
① SearXNG (localhost:8888)
   → 第一入口，大多数情况够用

② 直达权威页面（browser_navigate）
   → 搜到目标网站后直接进页面抓完整内容
   → 不依赖搜索结果摘要

③ mcp_minimax_plan_web_search
   → SearXNG 不够时启用
   → 注意高峰期（15:00-17:30）可能限流

④ 外国技术社区直搜
   → 技术问题：GitHub Issues > HuggingFace Discuss > StackOverflow
   → 产品体验：Reddit r/XX > DEV Community > Medium
   → 用 browser_navigate 进页面，不只看摘要

⑤ 第三方独立评测
   → Trustpilot / BestUSAVPS / LowEndBox 等
```

### 按类型的入口偏好

| 类型 | 必查 | 补充 |
|------|------|------|
| 技术 bug | GitHub Issues（官方） | StackOverflow |
| 技术选型/对比 | GitHub README + 官方文档 | 博客深度文 |
| AI 模型对比 | Artificial Analysis + LiveBench + Reddit | 第三方博客 |
| VPS/工具体验 | Trustpilot + Reddit r/VPS + BestUSAVPS | 独立博客 |
| AI Agent 框架 | GitHub Issues + r/openclaw + HuggingFace | DEV Community |
| 价格/套餐 | 官网 + 独立评测站 | Reddit 经验贴 |

---

## 三、搜索关键词规则

### 必用词

| 词 | 场景 |
|----|------|
| `site:github.com` | 精准搜 GitHub |
| `site:reddit.com` | 精准搜 Reddit |
| `site:huggingface.co` | 精准搜 HuggingFace |
| `site:stackoverflow.com` | 精准搜 StackOverflow |
| `intitle:"关键词"` | 精准匹配标题 |
| `"exact phrase"` | 精确短语匹配 |

### 优先不用

| 词 | 原因 |
|----|------|
| `site:zhihu.com` | VPS 出口 IP 被屏蔽，无效 |
| `site:baidu.com` | 同上 |
| 中文关键词搜英文资源 | 搜不到 |

### 多语言策略
- 搜英文资料 → Google/DuckDuckGo + 英文关键词
- 搜中文资料 → 百度/SearXNG 中文引擎
- 混合 → 先英文定位，再中文补充

---

## 四、研究流程

```
Step 1：确认问题类型，设定搜索深度
         ↓
Step 2：SearXNG 快速定位 3-5 个权威来源
         ↓
Step 3：按优先级逐个 browser_navigate 进页面抓完整内容
         ↓
Step 4：每抓完一个，问"够完整了吗"
         ↓ 不够 → 回 Step 2，换关键词继续挖
         ↓ 够 → Step 5
         ↓
Step 5：综合所有来源，整理完整报告
         ↓
Step 6：输出前检查——有没有某社区第一手内容还没挖到的？
```

---

## 五、停止标准

| 类型 | 停止条件 |
|------|---------|
| 快速事实类 | 找到明确答案，立即停止 |
| 技术实现类 | 2+ 独立来源给出相同方案，停止 |
| 产品选型类 | 1个详细评测 + 1个用户反馈 + 1个benchmark，停止 |
| 深度研究类 | 主要来源都已覆盖，新结果开始重复，停止 |
| 用户反馈类 | 同一缺点被 3+ 来源独立提到，停止 |

---

## 六、特殊规则

### 6.1 外国社区访问
- Reddit 在 VPS 上被屏蔽 → browser_navigate 直达，绕搜索摘要
- LowEndTalk 被 Cloudflare 拦截 → 换 LowEndBox 或 Trustpilot
- GitHub Issues/PRs → browser_navigate 进页面，不要只看搜索片段

### 6.2 给链接就要整理完整内容
- 用户没有明确说"我自己去看" → 必须 browser_navigate 进页面抓完整内容
- 不以搜索摘要作为最终答案来源

### 6.3 搜索轮数限制
- 单次任务最多 **3 轮搜索**（每轮可多工具并行）
- 超过 3 轮未解决 → 停下来汇报进度，问用户是否继续

---

## 七、研究前检查清单

- [ ] 问题类型已确认
- [ ] 搜索深度已设定
- [ ] 第一入口（SearXNG）已尝试
- [ ] 目标权威来源已定位
- [ ] browser_navigate 进页面抓完整内容（不是快速事实类时）
- [ ] 外国技术社区已查（技术/产品/选型问题时）
- [ ] 停止标准已核对
