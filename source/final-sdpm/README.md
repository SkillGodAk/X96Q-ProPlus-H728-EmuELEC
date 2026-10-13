# Final Standalone SD/MMC source delta

The accepted NoRoot image is the SD/MMC keep-awake build promoted after physical user acceptance.

Accepted image:
- H728_EmuELEC_4.8_Crystal_Standalone_20261013.img
- SHA256 97d67fb8d0cb0f27f7e3682a7a0be28d859a92ec522cb448d302b205f44036c9
- Final KERNEL SHA256 b482527b4ac808c0bff409859be2a380c682552e06aa85d1ab532246b988f74b
- Kernel config SHA256 e73aeb9a99ae78ac41c3e54bbca8ffc47b900714b128e74f2c04374767cc48d7

This directory preserves the scripts that made the final SD/MMC change and patched it into the accepted image. The exact final sunxi-mmc.c and its source report are stored beside these scripts.

Expected hashes:
- baseline sunxi-mmc.c: 885cb0dec475d25436a5602eb890b71a95c3bcb036b87b14e5dba4ccc674a01a
- final sunxi-mmc.c: 05b30029d76e1afd7ac12ac5b8eb856f3cc4c3f0d6c694e4604174635fdcc490
- prepare_boot_sd_keepawake_candidate.py: cbe61c749e9322ce8a407b684ce41e2dd4c284fc3f15ac089a73f593d60169b6
- build_boot_sd_keepawake_candidate.sh: 6de2711faefe91bd8e0e84f4e74fc4a57c09c2a92f181e049c9234538571ce93
- patch_existing_image_boot_sd_keepawake.py: 0f9faf1ecdbba8b88d803a1d7b6a912ce9dd7d0456ea35cbd1784a9607fec819

The remaining kernel board files and .config are in the SHA-verified selected board-source archive one directory above. Upstream kernel base: a90ee4305c4a5df72c11b31dacfdc76e00fcf78a.