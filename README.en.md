# X96Q Pro+ H728-EmuELEC 4.8

[繁體中文](README.md) · [简体中文](README.zh-CN.md) · [English](README.en.md)

An EmuELEC 4.8 integration for the **X96Q Pro+ (H728)** TV box. Two clean SD-card images with the Crystal theme, Traditional Chinese defaults, and first-boot FAT32 `EEROMS` game partition setup.

> **Compatibility warning:** Developed and evaluated primarily for the author's **original X96Q Pro+ H728** hardware. Other boxes labeled H728 may use different device trees, remote protocols, power circuits or boot paths. **They have not been verified and are not guaranteed to work.** Back up your SD card before flashing.

## Choose your edition

| Feature | **NoRoot — EmuELEC only** | **Root — Android + EmuELEC** |
| --- | --- | --- |
| Default boot | **EmuELEC** | **Original Android** |
| Android ROOT required? | **No** | **Yes, existing working `su`** |
| Original remote wake after shutdown | **Supported — wakes into EmuELEC** | **Supported — wakes into Android** |
| GameSwitch APK | Not needed | Required to enter EE from Android |
| First-boot FAT32 EEROMS expansion | Supported | Supported after entering EE |
| Crystal / game cores / controller setup | Supported | Supported |

**NoRoot DOES support waking the box with its original IR remote.** It wakes into EmuELEC rather than Android. Both editions have original-remote wake support, with different destinations.

**Special Root edition warning:** Compatibility has been designed and evaluated only for the **original X96Q Pro+ H728, its original Android environment, and its original IR remote**. Root means your existing Android can grant `su` access; this package **does not root Android**. Other H728 devices are untested, including their power management, boot behavior, and infrared remote support.

## H728-specific additions over a generic EmuELEC 4.8 setup

- H728 board boot-chain and device-tree integration, including AXP323 cold-start power initialization.
- Original IR remote shutdown and wake workflows: EE destination on NoRoot and Android destination on Root.
- Automatic first-boot creation and expansion of the FAT32 `EEROMS` game partition; no repeated formatting on later boots.
- Crystal theme and Traditional Chinese defaults, system folders, and 43 factory core files (games and BIOS are **not** provided).
- Android-to-EE switching and tailored reboot routing on the Root edition.

These describe this project's board-specific integration, not claims that every listed feature was invented here or absent from upstream EmuELEC 4.8.

## Downloads

Get the latest release from [GitHub Releases](../../releases):

| File | Purpose |
| --- | --- |
| `X96Q pro+_H728_EmuELEC_4.8_NoRoot.7z` | EmuELEC-only SD image |
| `X96Q pro+_H728_EmuELEC_4.8_Root.7z` | Android-first dual-boot SD image |
| `H728-GameSwitch.apk` | Root edition only; switch from Android into EE |

The two 7z files each extract to a 4 GiB IMG. Check the release checksums before flashing.

## Installation

1. Back up your SD card. Use 7-Zip to extract the **IMG** from the 7z archive.
2. Flash the IMG to the **correct SD card** using [balenaEtcher](https://etcher.balena.io/), then let verification finish. Never target your computer drive or the box's Android eMMC.
3. Power the box down and insert the card. NoRoot boots into EmuELEC. Root boots original Android first; on an already-rooted Android installation, install GameSwitch APK, grant the requested `su` permission, and use it to enter EE.
4. The first EE boot initializes the FAT32 `EEROMS` partition and factory files. **Do not unplug or reset during progress or expansion.**
5. Later boots must not reformat an existing EEROMS.

## Adding games

Once setup finishes, connect the SD card to a computer and open the FAT32 **`EEROMS`** partition. Put your legally obtained games into the appropriate per-system `roms` directories (for example `roms/nes`, `roms/snes`, or `roms/psx`; follow the folders actually present on your card). Some systems need compatible BIOS files, which you must provide legally and place in the relevant `bios` directory. Eject the card safely, return to EE, and refresh the game list. Preserve your saves and configuration.

## Important limitations

Only the original device combination has direct compatibility evidence. Other H728 devices, third-party remotes, and modified Android environments are unverified. This project does not provide copyrighted game ROMs, BIOS, or stock Android images; it does not gain ROOT access for you. Unofficial third-party integration; no endorsement by EmuELEC or the device vendor is implied.

