# X96Q Pro+ H728-EmuELEC 4.8

[繁體中文](README.md) · [简体中文](README.zh-CN.md) · [English](README.en.md)

这是针对 **X96Q Pro+（H728）** 整合的 EmuELEC 4.8 双版本纯净映像，默认采用 Crystal 主题、繁体中文，并支持首次创建 FAT32 `EEROMS` 游戏分区。

> **兼容性提示**：主要在作者的 X96Q Pro+ H728 原机上进行开发和验证。其他标示 H728 的盒子可能使用不同的设备树、红外遥控器及电源配置，**未实测，不保证兼容**。刷写之前务必备份 SD 卡。

## Root 与 NoRoot 有什么区别？

| 功能 | **NoRoot：纯 EmuELEC** | **Root：Android + EmuELEC** |
| --- | --- | --- |
| 默认开机 | **EmuELEC** | **原机 Android** |
| 是否需要 Android ROOT | **不需要** | **需要 Android 现有的 `su` 权限** |
| 原装遥控器关机后唤醒 | **支持，进入 EmuELEC** | **支持，进入 Android** |
| GameSwitch APK | 不需要 | 需要，通过 Android 切换进 EE |
| 首次自动创建 FAT32 EEROMS | 支持 | 进入 EE 后支持 |
| Crystal、繁中、游戏核心、手柄设置 | 支持 | 支持 |

**重要：NoRoot 同样支持原装遥控器关机后唤醒。** 两个版本的差异只是唤醒后的目标系统不同。

**Root 特别说明**：仅针对**原款 X96Q Pro+ H728、原厂 Android 环境与原装遥控器**验证。这里的 ROOT 是指 Android 本来就可以授权 `su`，不代表本项目会为 Android 获取 ROOT。其他 H728 盒子可能存在不同的启动方式及红外唤醒机制，未经过测试，不能保证工作。

## 相比通用 EmuELEC 4.8 的 H728 整合

- 针对 H728 的启动链、设备树和 AXP323 冷启动电源初始化。
- 原装遥控器关机及红外唤醒：NoRoot 唤醒回 EE，Root 唤醒回 Android。
- 首次创建／扩容 FAT32 `EEROMS`，正常重启不会重新格式化。
- Crystal 默认主题、繁体中文设置、43 个工厂核心文件及游戏目录。
- Root 版 Android／EE 切换与对应重启逻辑。

以上是本项目的 H728 整合内容，并不是声称这些都是 EmuELEC 4.8 中从未存在过的功能。

## 下载与安装

从 [GitHub Releases](../../releases) 下载：`X96Q pro+_H728_EmuELEC_4.8_NoRoot.7z`（纯 EE）、`X96Q pro+_H728_EmuELEC_4.8_Root.7z`（Android＋EE）以及仅供 Root 版使用的 `H728-GameSwitch.apk`。每个压缩包解压后都是 4 GiB 的 IMG。

1. 备份 SD 卡，用 7-Zip 解压 `.7z`，获得 `.img`。
2. 使用 [balenaEtcher](https://etcher.balena.io/) 选择 IMG 和正确 SD 卡，烧录并完成验证。**不要选择电脑系统盘或 Android eMMC。**
3. NoRoot 插卡开机进入 EE；Root 插卡后默认进入原机 Android，在 Android 已有 ROOT／`su` 授权下安装 GameSwitch APK，切换进入 EE。
4. 首次进入 EE 时，等待创建和扩容 FAT32 `EEROMS` 以及核心初始化完成。不要在此过程中断电或拔卡。
5. 之后正常重启，不应该再次格式化已经建立的 EEROMS。

## 如何添加游戏？

初始化完成后，将 SD 卡连接电脑，打开 FAT32 `EEROMS` 分区。把你合法持有的游戏文件按平台放在对应的 `roms` 目录（例如 `roms/nes`、`roms/snes`、`roms/psx`，以实际生成的目录为准）。某些平台需要自行准备合法的 BIOS 文件，放在对应的 `bios` 位置。安全弹出卡片并返回 EE，刷新游戏列表。请先备份存档，不要覆盖自己的游戏数据。

## 限制说明

本项目不提供游戏 ROM、BIOS 或原厂 Android 映像；不保证其他 H728 盒子、第三方遥控器或非原厂 Android 的兼容性。Root 版需要现有 Android `su`，不负责获取 ROOT。此项目不是 EmuELEC 或盒子厂商的官方作品。

## 支持作者

如果项目对你有帮助，欢迎自愿赞助：

**海外赞助：** [Buy Me a Coffee](https://buymeacoffee.com/SkillGodAK)

[![Buy Me a Coffee](https://raw.githubusercontent.com/SkillGodAk/DRO/main/assets/donate-buymeacoffee.svg)](https://buymeacoffee.com/SkillGodAK)

**银行收款：**

![银行赞助 QR Code](https://raw.githubusercontent.com/SkillGodAk/DRO/main/assets/donate-bank.jpg)

**微信收款：**

![微信收款 QR Code](https://raw.githubusercontent.com/SkillGodAk/DRO/main/assets/donate-wechat.jpg)

---

第三方非官方开源整合。对应源代码与许可见 [SOURCE-AND-LICENSES.md](SOURCE-AND-LICENSES.md)。
