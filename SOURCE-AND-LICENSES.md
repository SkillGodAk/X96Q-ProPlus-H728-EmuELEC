# Source availability and licensing / 原始碼與授權

This project combines independent board-specific integration with upstream open-source software, including components based on EmuELEC, the Linux kernel, U-Boot, Arm Trusted Firmware, and other packages. Upstream authors retain their copyright and respective licenses.

**Distribution requirement:** Before distributing modified GPL-covered kernel or bootloader binaries, make the **complete corresponding source code**, including board-specific modifications, configuration and build scripts needed to regenerate those particular binaries, available under the applicable licenses. A link to unrelated upstream HEAD is not sufficient if the distributed binaries contain local patches.

- Published and SHA-verified **H728 board source snapshot and formal rebuild inputs**: [source/README.md](source/README.md), with exact upstream revisions, local source/config hashes and build helpers tied to the released image hashes.
- Published **EmuELEC 4.8 local board modifications**: [H728 EmuELEC 4.8 patches and overlays](source/emuelec-4.8/README.md).
- Published final SD/MMC source delta and rebuild helpers: [final-sdpm](source/final-sdpm/), [core-build](source/core-build/), and [Root image rebuild](source/dualboot-rebuild/).
- Formal source audit manifest: [SOURCE_AUDIT_20261014.json](source/SOURCE_AUDIT_20261014.json). It ties the two formal image hashes to the exact upstream revisions and H728-local source/config/build inputs.
- The EmuELEC 4.8 tree at the pinned upstream commit remains the base for unchanged package sources; H728-local EmuELEC changes are published under [source/emuelec-4.8](source/emuelec-4.8/). No game ROM or BIOS content is distributed by this project.
- Build commit hashes and local patch/source lists are recorded in [SOURCE_AUDIT_20261014.json](source/SOURCE_AUDIT_20261014.json) and [FORMAL_BUILD_MANIFEST.json](source/FORMAL_BUILD_MANIFEST.json).
- H728-GameSwitch.apk is a project-owned helper, not a third-party APK; its source representation is published in [source/gameswitch-apk](source/gameswitch-apk/).

The download archives contain SD-card images only. No commercial game ROMs, BIOS or vendor Android system images are separately provided. An SD image may contain upstream software subject to additional notices and licenses.

**繁體中文**：本倉庫已公開正式版使用的精確上游版本、H728 本地修改來源、組態、建置／映像重建腳本與 GameSwitch APK 來源。各上游與第三方元件仍依各自授權條款提供；本頁是來源與授權對照，不取代各元件原始授權文字。
