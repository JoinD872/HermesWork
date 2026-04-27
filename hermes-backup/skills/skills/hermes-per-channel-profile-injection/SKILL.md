---
name: hermes-per-channel-profile-injection
description: Hermes 多群聊（飞书/Telegram/Discord）按 chat_id 注入独立 Profile SOUL.md + MEMORY.md 的完整方案。核心原理：Gateway 单实例不加载 per-profile SOUL/MEMORY，需通过 channel_prompt 字段注入。
category: hermes
---

# Hermes Per-Channel Profile SOUL + Memory 注入

## 背景问题

Hermes Gateway 是单实例，运行在 `default` profile 下，**永远只加载全局文件**：
- `~/.hermes/SOUL.md`
- `~/.hermes/memories/MEMORY.md`

各 profile 目录下的 `profiles/<name>/SOUL.md` 和 `profiles/<name>/memories/MEMORY.md` **根本不会被 gateway 加载**。重启 gateway 无济于事。

## 正确架构：channel_prompt 注入

所有支持多 channel 的 platform adapter（Telegram / Discord / Slack）都已实现：通过 `MessageEvent.channel_prompt` 字段注入 per-channel/per-chat_id 的额外 system prompt。

**消息流程：**
```
飞书消息到达
  → FeishuAdapter._on_message_event()
  → 构建 MessageEvent(chat_id, channel_prompt=???)  ← 注入点
  → Gateway run_sync()
  → combined_ephemeral = context_prompt + channel_prompt + ephemeral_system_prompt
  → AIAgent(ephemeral_system_prompt=combined_ephemeral)
  → LLM 收到正确的 persona prompt
```

**`channel_prompt` 字段**（`gateway/platforms/base.py` MessageEvent dataclass）：
- `MessageEvent.channel_prompt: Optional[str]` — per-channel 临时 system prompt
- 在 `gateway/run.py` 的 `run_sync()` 里拼入 `combined_ephemeral`
- 每次消息单独注入，不污染 session history

## 实现步骤（以 Feishu 为例）

### 1. 添加 `_resolve_profile_channel_prompt` 方法

在 `gateway/platforms/feishu.py` 的 `FeishuAdapter` 类中添加：

```python
def _resolve_profile_channel_prompt(self, chat_id: str) -> str:
    """Resolve per-chat_id profile SOUL.md + MEMORY.md as channel_prompt."""
    from pathlib import Path
    import os

    # chat_id → profile name（与 system prompt 路由表一致）
    _profile_map = {
        "oc_cc9c8289c9520ff326578703ff17392c": "vps-technician",
        "oc_5a883cbe523b1a93ee269bba2f8536a0": "game-designer",
        "oc_6dbf15aa718c29adca8d085017930a71": "health",
        "oc_ec9adb3139cd38ac706cd7a54c4d059d": "researcher",
    }

    profile_name = _profile_map.get(chat_id)
    if not profile_name:
        return ""

    hermes_root = Path(os.path.expanduser("~/.hermes"))
    profile_dir = hermes_root / "profiles" / profile_name

    if not profile_dir.is_dir():
        return ""

    parts = []
    soul_path = profile_dir / "SOUL.md"
    if soul_path.is_file():
        content = soul_path.read_text(encoding="utf-8").strip()
        if content:
            parts.append(content)

    memory_path = profile_dir / "memories" / "MEMORY.md"
    if memory_path.is_file():
        content = memory_path.read_text(encoding="utf-8").strip()
        if content:
            parts.append(content)

    return "\n\n".join(parts)
```

### 2. 注入到所有 MessageEvent 创建点

在 `feishu.py` 中找到所有 `MessageEvent(` 构造处，添加 `channel_prompt` 参数：

```python
# 普通文本消息
normalized = MessageEvent(
    ...
    channel_prompt=self._resolve_profile_channel_prompt(chat_id) or None,
)

# reaction 合成事件（如有）
synthetic_event = MessageEvent(
    ...
    channel_prompt=self._resolve_profile_channel_prompt(chat_id) or None,
)

# card action 合成事件（如有）
synthetic_event = MessageEvent(
    ...
    channel_prompt=self._resolve_profile_channel_prompt(chat_id) or None,
)
```

**必须全部处理**，不能只改普通消息路径。合成事件（reaction、card button）如果不注入，走的是不带 persona 的裸 system prompt。

### 3. 验证语法

```bash
cd ~/.hermes/hermes-agent
python -m py_compile gateway/platforms/feishu.py
```

### 4. 重启 gateway

```bash
hermes gateway restart
# 或
systemctl --user restart hermes-gateway
```

## 关键教训

1. **重启不解决 SOUL/MEMORY 不加载的问题** — 因为根本没在这个加载路径上
2. **profile 目录的 SOUL/MEMORY 是给 `hermes chat --profile <name>` 用的**，不是给 gateway 消息用的
3. **channel_prompt 机制** 是 platform adapter 层的注入点，Telegram/Discord/Slack 早已用这个方式实现 per-channel 提示词
4. **Feishu adapter 在实现时遗漏了这个机制**，需要手动补全

## 参考：Telegram/Discord 的 channel_prompt 用法

Telegram（`gateway/platforms/telegram.py`）:
```python
_channel_prompt = resolve_channel_prompt(self.config.extra, thread_id_str or _chat_id_str, ...)
return MessageEvent(..., channel_prompt=_channel_prompt)
```

Discord（`gateway/platforms/discord.py`）:
```python
_channel_prompt = self._resolve_channel_prompt(channel_id, parent_id)
return MessageEvent(..., channel_prompt=_channel_prompt)
```

`resolve_channel_prompt()` 定义在 `gateway/platforms/base.py`，它查 `config.extra.get("channel_prompts")` dict。本方案直接读 profile 文件，效果相同但更易维护。
