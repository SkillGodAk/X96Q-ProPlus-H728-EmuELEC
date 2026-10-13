# Root Android-first image rebuild scripts

The Root image is derived from the accepted Standalone SDPM image without rebuilding its kernel or P2 from unrelated sources.

Final image:
- H728_EmuELEC_4.8_Crystal_DualBoot_20261013.img
- SHA256 f7340855da489c164fc4b0994ec13f56a357a95a1b393d57496f424a38c552b3
- Base Standalone SHA256 97d67fb8d0cb0f27f7e3682a7a0be28d859a92ec522cb448d302b205f44036c9

This folder preserves the actual image builder, policy tests, free-space scrubber and final FAT FSInfo normalization used for the accepted Android-first image. H728-GameSwitch.apk is distributed as the separate signed Release asset.

The Root image changes the SD boot route and P2 switching helpers while keeping the accepted kernel, SYSTEM, DTB and EmuELEC source base. See ../final-sdpm/ and ../emuelec-4.8/ for the corresponding source inputs.