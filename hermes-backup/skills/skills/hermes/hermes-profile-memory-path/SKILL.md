---
description: Hermes Agent profile 专属 SOUL/MEMORY 路径规范 — 读取自己的 soul 和 memory 时必须用 profile 路径，不能读全局 ~/.hermes/memories/
name: hermes-profile-memory-path
---

# Hermes Agent — Profile 专属 SOUL/MEMORY 路径规范

## 触发条件

当你需要读取自己（当前 Agent）的 SOUL 或 MEMORY 时，必须使用 **profile 专属路径**，而不是全局路径 `~/.hermes/memories/`。

## 路径规则

| 文件 | 正确路径 | 错误路径（勿用） |
|------|---------|----------------|
| SOUL.md | `~/.hermes/profiles/<profile_name>/SOUL.md` | `~/.hermes/SOUL.md` |
| MEMORY.md | `~/.hermes/profiles/<profile_name>/memories/MEMORY.md` | `~/.hermes/memories/MEMORY.md` |
| config.yaml | `~/.hermes/profiles/<profile_name>/config.yaml` | - |

**当前 Agent 的 profile_name**：从 SOUL.md 第一行或路由规则中确认。例如 VPS 技术助手是 `vps-technician`。

## 为什么不能读全局路径

- `~/.hermes/memories/MEMORY.md` 是**全局/共享 memory**，给没有专属 profile 的 Agent 用或作为 fallback
- 每个专属 Agent（老V/小策/小健/小研）的 memory 在 `~/.hermes/profiles/<name>/memories/MEMORY.md`
- 两者内容可能不同，读错会导致看到别的 Agent 的记忆、用过时/错误的信息

## 验证步骤

读取前先用 `search_files` 或 `ls` 确认路径存在：

```bash
ls ~/.hermes/profiles/<profile_name>/
ls ~/.hermes/profiles/<profile_name>/memories/
```

## 已知 profile 列表（2026-04）

- `vps-technician` — VPS 技术助手（老V）
- `researcher` — 凌晨研究员（小研）
- `game-designer` — 游戏制作搭档（小策）
- `health` — 健康顾问（小健）
