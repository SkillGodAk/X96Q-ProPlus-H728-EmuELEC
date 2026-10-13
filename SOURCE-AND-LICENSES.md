# Source availability and licensing / 原始碼與授權

This project combines independent board-specific integration with upstream open-source software, including components based on EmuELEC, the Linux kernel, U-Boot, Arm Trusted Firmware, and other packages. Upstream authors retain their copyright and respective licenses.

**Distribution requirement:** Before distributing modified GPL-covered kernel or bootloader binaries, make the **complete corresponding source code**, including board-specific modifications, configuration and build scripts needed to regenerate those particular binaries, available under the applicable licenses. A link to unrelated upstream HEAD is not sufficient if the distributed binaries contain local patches.

- Published and SHA-verified **partial board source**: [H728 source snapshot and manifest](source/README.md).
- Published **EmuELEC 4.8 local board modifications**: [H728 EmuELEC 4.8 patches and overlays](source/emuelec-4.8/README.md).
- **Still pending:** independent validation that these files, upstream revisions and any remaining local modifications comprise the COMPLETE corresponding source and scripts for all GPL-covered binaries in both firmware images. Do not represent the source requirement as finished yet.
- Build commit hashes and patch lists: **PENDING source audit**.
- Third-party APK licensing and inclusion must be checked before public distribution.

The download archives contain SD-card images only. No commercial game ROMs, BIOS or vendor Android system images are separately provided. An SD image may contain upstream software subject to additional notices and licenses.

**繁體中文**：公開發布修改過的 Linux／U-Boot 等 GPL 元件二進位時，必須提供與該版實際成品相對應的完整原始碼及必要的修改與組態。對應版本尚未稽核／公布完成，請勿將此文件當成已履行授權義務的證明。
