# Core build and clean-image reproduction helpers

This directory preserves the build helpers used around the accepted H728 kernel/boot source and the clean Standalone image.

Exact upstream revisions:
- Linux: torvalds/linux a90ee4305c4a5df72c11b31dacfdc76e00fcf78a
- U-Boot: u-boot/u-boot a6ab6a66146ed0bf1420db0ee858b49005783222
- Arm Trusted Firmware: jernejsk/arm-trusted-firmware b5de74a685fb73b784e45bbbd18dd9a0c528d8b2
- EmuELEC 4.8: EmuELEC/EmuELEC 02b45fe53b85c45c75dbad8e44a648092dec2e72

The SHA-verified local source snapshots and kernel config are in ../h728-selected-board-sources-20261014.tar.gz. The final SD/MMC delta is in ../final-sdpm/. EmuELEC local modifications are in ../emuelec-4.8/.

Helper SHA256:
- build_clean_release.sh: 8cb4dc7b6c6f1947cc985ecbd99d3c13db573a865db896de3c6f9113ce4fd13c
- clean_release_prepare.py: 0bf9a76d809f26216ac1f479287ae5d059bc11122e9c9ed25e72524a9f16738d
- h728_build_axp323_guest.sh: 6ab598d7d34018c1f56d8cacb50b98e53397afdbb4ea97305401a6d73857cf65
- prepare_crystal_only_release.py: 58584eeff83c57089d56bd233334078caa25ebf3aceac5b8ae7896cdcb6a3ce0
- rebuild_clean_standalone_20261013.py: d6db555af302d9017e33d4854be40b5b5d857eb1a3e3b9d3cb7ed90a14f63fe2

The original development environment used Ubuntu 22.04.5 with Docker 29.1.3. A private Docker image backup is retained for reproducibility but is not an end-user Release asset. These scripts contain historical staging paths; use the documented SHA values rather than assuming those paths exist on another machine.