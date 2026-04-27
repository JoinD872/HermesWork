---
name: pokemon-player
description: 宝可梦模拟器自动对战 — 通过 PokeEngine API 控制 PokePaste 宝可梦队伍，支持 Showdown 格式，自动选宠/发动招式/动态决策
version: 1.0.0
tags: [gaming, pokemon, emulator, automation, showdown]
---

# Pokemon Player Skill

通过 PyBoy 模拟器无头运行宝可梦红/蓝/黄版，基于 RAM 状态读取实现自动寻路、对战、存档。支持道馆顺序策略和动态战斗决策。

## 核心功能

- **RAM 状态读取**：直接读取模拟器内存获取宝可梦数据、位置、战斗状态
- **自动对战**：根据对手宝可梦类型动态选择招式
- **导航系统**：自动寻路，处理建筑出口陷阱和地图转换等待
- **存档管理**：自动存档/读档

## 使用方式

此 skill 需要通过 `delegate_task` 配合独立的 python 子进程运行，因为需要持久化模拟器状态。

## 依赖

- PyBoy 模拟器
- PokeEngine API
- 宝可梦 ROM（需自行提供）
