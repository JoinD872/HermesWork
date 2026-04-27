---
name: session-reset-image-recovery
description: After session auto-reset, recover context from screenshots using mcp_minimax_plan_understand_image instead of vision_analyze.
---
# Session Reset Image Recovery

## Problem
After session auto-reset (204K tokens), conversation history is lost. User sends a chat screenshot to restore context.

## Solution
Use `mcp_minimax_plan_understand_image` instead of `vision_analyze`.

```python
mcp_minimax_plan_understand_image(
  image_source="/home/wjj/.hermes/image_cache/img_d9e83164fb58.jpg",
  prompt="请详细描述这张聊天截图的完整内容，包括所有消息文本、上下文和时间"
)
```

## Key Finding
- `vision_analyze` does NOT work for me (always returns "I don't see any image")
- `mcp_minimax_plan_understand_image` works correctly

## Important Context Recovery Lesson
After session reset, do NOT trust old conversation context. Re-examine actual current state:
- Check config files directly (don't assume what was said in chat happened)
- Verify what the user actually said vs. what you thought was happening
- The previous session may have been interrupted mid-task, so "todo" from old context may not have actually been completed

## Example Flow
1. User sends screenshot → use mcp_minimax_plan_understand_image to read it
2. Cross-reference screenshot claims against actual current files/config
3. Only proceed with "pending tasks" if they're actually still pending in reality
