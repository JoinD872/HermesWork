---
name: memory-reset-recovery
description: Session auto-reset recovery — what survives, what doesn't, and how to restore context quickly
triggers:
  - "session reset"
  - "conversation cleared"
  - "历史被清空"
  - "重新开始了"
---

# Memory Reset Recovery

## When this happens
Session auto-resets due to token limit (~200K), network interrupt, or timeout. Conversation history is cleared.

## Immediate response
1. Check memory with `memory(action='list')` — key info survives reset
2. Tell user what happened briefly
3. Load critical context from memory
4. Ask if they want to continue previous topic

## What survives reset
- **Memory** — persistent across sessions (user profile, tech debt, important facts)
- **Skills** — stored in `~/.hermes/skills/`, permanent
- **Learnings files** — `.learnings/LEARNINGS.md`, `.learnings/ERRORS.md`, etc.

## What doesn't survive
- Current conversation history
- Active session context

## Prevention
- Long conversations: proactively save key facts to Memory
- Complex tasks: save approach as Skill when done
- User says "remember this": immediately `memory(action='add')`

## Memory management
Memory has a ~2,200 char limit. When full:
1. `memory(action='list')` to find verbose/split entries to consolidate
2. `memory(action='replace')` with multi-line old_string often fails — use single-line exact match
3. `memory(action='remove', old_text='...')` with single-line old_string works reliably
4. Remove one entry at a time until space is freed

## MCP tools verification
MCP server running ≠ tools available. Try calling the tool — if "not found", MCP didn't register.
Gateway may need restart after config change for MCP to take effect.

## Image analysis
Use `vision_analyze(image_url='/home/wjj/.hermes/image_cache/img_xxx.jpg', question='...')` for local images.
If vision says "no image", verify file is valid: `file {path}`

## Key memory entries to maintain
- User profile (name, role, environment, contact)
- Tech debt / unresolved issues
- Active project context
- User preferences (communication style, pet peeves)
