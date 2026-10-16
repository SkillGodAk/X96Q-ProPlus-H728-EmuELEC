# X96Q Pro+ H728-EmuELEC 4.8

[繁體中文](README.md) · [简体中文](README.zh-CN.md) · [English](README.en.md)

An EmuELEC 4.8 integration for the **X96Q Pro+ (H728)** TV box. Two clean TF-card images with the Crystal theme, Traditional Chinese defaults, and first-boot FAT32 `EEROMS` game partition setup.

> **Compatibility warning:** Developed and evaluated primarily for the author's **original X96Q Pro+ H728** hardware. Other boxes labeled H728 may use different remotes or boot behavior. **They have not been verified and are not guaranteed to work.** Back up your TF card before flashing.

## Choose your edition

| Feature | **NoRoot — EmuELEC only** | **Root — Android + EmuELEC** |
| --- | --- | --- |
| Default boot | **EmuELEC** | **Original Android** |
| Android ROOT required? | **No** | **Yes, original Android must already be rooted** |
| Original remote wake after shutdown | **Supported — wakes into EmuELEC** | **Supported — wakes into Android** |
| Original remote controls (Up/Down/Left/Right, Back, OK) | Supported | Supported |
| Bluetooth | Supported | Supported |
| One-to-two controller recognition (two gamepads) | Supported | Supported |
| GameSwitch APK | Not needed | Required to enter EE from Android |
| Automatic EEROMS game storage | Supported | Supported after entering EE |
| Crystal / emulators / controller setup | Supported | Supported |

**NoRoot DOES support waking the box with its original IR remote.** It wakes into EmuELEC rather than Android. Both editions have original-remote wake support, with different destinations.

**Special Root edition warning:** Compatibility has been designed and evaluated only for the **original X96Q Pro+ H728, its original Android environment, and its original IR remote**. Root requires an already-rooted original Android installation; this package **does not root Android**. Other H728 devices are untested, including their power management, boot behavior, and infrared remote support.

## What's different from a regular EmuELEC 4.8 setup?

- **Made ready for X96Q Pro+**: Boot EmuELEC from an TF card without having to figure out the box-specific setup yourself.
- **Use the original remote to shut down and wake the box**: NoRoot wakes into EmuELEC; Root wakes back into Android.
- **Original remote navigation**: Use Up, Down, Left and Right to move around, with Back and OK to select and return.
- **Bluetooth support**: Use the Bluetooth connection features built into the system.
- **Two-controller recognition**: Supports one-to-two gamepad recognition, with controller settings available for both gamepads.
- **Game storage sets itself up**: On the first EmuELEC start, the game partition is prepared for your TF card's capacity. Later boots don't repeat the setup.
- **A familiar interface from the start**: Crystal theme, Traditional Chinese defaults, game folders, and included emulator cores. Bring your own games and any required BIOS files.
- **Keep Android available**: With Root, use the GameSwitch APK in the original Android system to enter EmuELEC.

## Downloads

Download the latest release from [GitHub Releases](../../releases):

| File | Purpose |
| --- | --- |
| `X96Q pro+_H728_EmuELEC_4.8_NoRoot.7z` | EmuELEC-only SD image |
| `X96Q pro+_H728_EmuELEC_4.8_Root.7z` | Android-first dual-boot SD image |
| `H728-GameSwitch.apk` | Root edition only; switch from Android into EE |

The two 7z files each extract to a 4 GiB IMG. Check the release checksums before flashing.

## Installation

1. Back up your TF card. Use 7-Zip to extract the **IMG** from the 7z archive.
2. Flash the IMG to the **correct TF card** using [balenaEtcher](https://etcher.balena.io/), then let verification finish. Never target your computer drive or the box's Android eMMC.
3. Power the box down and insert the card. NoRoot boots into EmuELEC. Root boots original Android first; on an already-rooted Android installation, install GameSwitch APK, grant the requested `su` permission, and use it to enter EE.
4. The first EE boot initializes the FAT32 `EEROMS` partition and factory files. **Do not unplug or reset during progress or expansion.**
5. Later boots must not reformat an existing EEROMS.

## Adding games

Once setup finishes, connect the TF card to a computer and open the FAT32 **`EEROMS`** partition. Put your legally obtained games into the appropriate per-system `roms` directories (for example `roms/nes`, `roms/snes`, or `roms/psx`; follow the folders actually present on your card). Some systems need compatible BIOS files, which you must provide legally and place in the relevant `bios` directory. Eject the card safely, return to EE, and refresh the game list. Preserve your saves and configuration.

## Important limitations

Only the original device combination has direct compatibility evidence. Other H728 devices, third-party remotes, and modified Android environments are unverified. This project does not provide copyrighted game ROMs, BIOS, or stock Android images; it does not gain ROOT access for you. Unofficial third-party integration; no endorsement by EmuELEC or the device vendor is implied.

## Support the author

If this project has been helpful, you can support its independent development.

**International donations:**

<a href="https://buymeacoffee.com/SkillGodAK"><img src="assets/donate-buymeacoffee.svg" alt="Buy Me a Coffee" width="180"></a>

**WeChat donation:**

<img src="assets/donate-wechat.jpg" alt="WeChat donation QR code" width="180">

---

Unofficial third-party integration. Open-source notices and corresponding-source information: [SOURCE-AND-LICENSES.md](SOURCE-AND-LICENSES.md).
