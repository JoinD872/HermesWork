---
name: hermes-session-browser-tool-diagnostics
description: Hermes Agent — browser tool 弹窗/超时诊断流程，通过扫 session JSONL 和日志定位真实问题
tags: [hermes, browser-tool, troubleshooting, session-analysis]
last_updated: 2026-04-25
---

# Hermes Browser Tool 诊断流程

## 触发条件
排查 browser tool 弹窗卡住、timeout、CDP 报错时使用。

---

## 步骤一：查结构化日志（立即有结果）

```bash
cat /root/.hermes/logs/errors.log | grep -i browser
cat /root/.hermes/logs/agent.log | grep -i browser
cat /root/.hermes/logs/gateway-stderr.log | grep -i browser
```

无输出 = 进程级无 browser 报错。

---

## 步骤二：扫所有 session JSONL（找实际调用失败）

```bash
for f in /root/.hermes/sessions/*.jsonl; do
  result=$(python3 -c "
import json, sys
errors = []
try:
    with open('$f') as fh:
        for line in fh:
            try:
                obj = json.loads(line)
                if obj.get('role') == 'tool' and obj.get('content'):
                    text = str(obj['content'])
                    if ('error' in text.lower() or 'failed' in text.lower() or 'timeout' in text.lower()) and ('browser' in text.lower() or 'cdp' in text.lower() or 'snapshot' in text.lower() or 'navigate' in text.lower()):
                        errors.append(text[:200])
            except: pass
    if errors:
        print(f'$f: {len(errors)} error(s)')
        for e in errors[:3]:
            print('  ', e[:150])
except: pass
" 2>/dev/null)
  if [ -n "$result" ]; then echo "$result"; fi
done
echo "扫描完成"
```

---

## 步骤三：分析错误类型

扫出的"error"大多数是以下几类，**不是 browser tool 本身的问题**：

| 错误类型 | 原因 | 是否需处理 |
|---------|------|-----------|
| `Non-JSON output from agent-browser` | agent-browser 正常输出被误判为错误 | ❌ 忽略 |
| Epic 403/Cloudflare 封锁 | VPS 出口 IP 被屏蔽 | ⚠️ 换工具/代理，非 Hermes 问题 |
| `Skill 'xxx' not found` | skill 名称拼写错误 | ❌ 跟 browser 无关 |
| `cdp_url` 连接失败 | 端口/进程问题 | ✅ 需处理 |

**真正的弹窗问题**特征：session 中出现 `cookie banner`、`notification prompt` 等字样但未报 timeout，说明 v0.10.0 遇到但未处理。

---

## 步骤四：判断是否需要升级 v0.11.0

v0.11.0 的 CDP supervisor 会自动处理：
- Cookie banner 遮罩交互按钮
- 浏览器 notification 弹窗
- 其他覆盖层对话框

如果诊断发现频繁遇到弹窗场景 → 升 v0.11.0。
如果只是 IP 封锁（403/Cloudflare）→ 升级解决不了，换工具。

---

## 关键路径

| 文件 | 用途 |
|-----|------|
| `/root/.hermes/sessions/*.jsonl` | 26 个 session，最早 4月20日 |
| `/root/.hermes/logs/errors.log` | 进程级错误日志 |
| `/root/.hermes/logs/agent.log` | Agent 运行日志 |
| `/root/.hermes/logs/gateway-stderr.log` | Gateway stderr |
| `~/.hermes/profiles/*/config.yaml` 的 `browser:` 小节 | Browser 配置 |
