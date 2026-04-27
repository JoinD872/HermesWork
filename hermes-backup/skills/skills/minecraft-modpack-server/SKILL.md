---
name: minecraft-modpack-server
description: Modded Minecraft 服务器搭建 — 从 CurseForge/Modrinth server pack zip 启动，NeoForge/Forge 安装/Java 版本/JVM 调优/防火墙/备份/启动脚本
version: 1.0.0
tags: [gaming, minecraft, modded-server, curseforge, modrinth, neoforge]
---

# Minecraft Modpack Server Skill

从 CurseForge 或 Modrinth server pack zip 搭建 modded Minecraft 服务器。

## 支持的 Mod Loader

- NeoForge（推荐，现代 mod）
- Forge（传统 mod）

## 流程

1. 选择并下载 server pack（CurseForge / Modrinth）
2. 安装 Java（推荐 Java 21 / Java 17）
3. 配置 JVM 参数（内存/GC）
4. 配置防火墙（默认 25565）
5. 设置启动脚本
6. 配置自动备份

## JVM 调优

```bash
# 典型 4GB 内存配置
java -Xmx4G -Xms4G -XX:+UseG1GC \
  -jar neoforge-installer.jar --installServer
```

## 备份建议

- 每日自动备份 world 文件夹
- 备份前停止服务器
- 保留最近 7 天备份

## LAN 配置

如需局域网多人游戏，配置端口转发或使用 ngrok。
