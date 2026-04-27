---
name: cron-archival
description: Cron 任务文件归档机制 — 研究报告按日期自动归档，防止文件无限膨胀，适用于 Hermes cron 任务写大文件的场景
---

# Cron 任务文件归档机制

## 触发条件
Cron 任务每次运行需要写入报告文件，且该文件会随时间无限增长。

## 核心问题
Cron session 没有持久上下文，不能依赖"上次记住"。如果报告文件（如 `research_results.md`）每次都是覆盖写入，旧的就被覆盖丢失；如果追加写入，文件会无限膨胀。

## 解决方案：归档 + 模板化

### 目录结构
```
memories/
├── research_results.md    # 永远只有最新一份（覆盖写入）
├── research_archive/      # 按日期归档历史
│   ├── 2026-04-24.md
│   ├── 2026-04-23.md
│   └── ...
└── pending.md             # 任务队列
```

### cron prompt 中的归档步骤（必须每次执行）

放在"读取任务"之后、"写入报告"之前，用 terminal() 执行：

```bash
ARCHIVE_DIR=~/.hermes/profiles/researcher/memories/research_archive
DATE=$(date +%Y-%m-%d)
if [ -s ~/.hermes/profiles/researcher/memories/research_results.md ]; then
  cp ~/.hermes/profiles/researcher/memories/research_results.md "$ARCHIVE_DIR/${DATE}.md"
fi
```

### 报告文件模板（初始状态）

```markdown
# 小研研究结果报告
**研究员**：小研（凌晨研究员）
**触发方式**：Cron 自动执行

---
*归档机制已建立，旧报告按日期存档于 `research_archive/` 目录*
```

## cron 内标准执行顺序
1. 读取 pending.md / tasks.md 获取任务
2. **执行归档**（先搬走旧文件）
3. 执行研究/工作
4. 写入报告（覆盖）
5. 推送通知（飞书等）
6. 退出

## 验证命令
```bash
ls -lh ~/.hermes/profiles/researcher/memories/research_archive/
wc -c ~/.hermes/profiles/researcher/memories/research_results.md
```

## 适用场景
- 研究员 agent 的研究结果报告
- 任何 cron 跑的定期报告任务
- 文件会随时间持续增长的工作流
