#!/bin/bash
set -euo pipefail
S=/home/ubuntu/h728-cold-start-20261012
cd "$S"
test ! -e boot-sd-keepawake-build-r2.log
exec >boot-sd-keepawake-build-r2.log 2>&1
trap 'rc=$?; printf "%s\n" "$rc" > boot-sd-keepawake-build-r2.rc' EXIT
test "$(sha256sum kernel-handoff-source/.config | cut -d' ' -f1)" = e73aeb9a99ae78ac41c3e54bbca8ffc47b900714b128e74f2c04374767cc48d7
if test ! -f boot-sd-keepawake-source-report.json; then
 python3 prepare_boot_sd_keepawake_candidate.py "$S/kernel-handoff-source"
else
 python3 -c 'import hashlib,json,pathlib; s=pathlib.Path("."); r=json.loads((s/"boot-sd-keepawake-source-report.json").read_text()); assert hashlib.sha256((s/"kernel-handoff-source/drivers/mmc/host/sunxi-mmc.c").read_bytes()).hexdigest()==r["candidate_sha256"]'
fi
docker run --rm --network none --user "$(id -u):$(id -g)" \
 -e CCACHE_DISABLE=1 -e PATH=/build/build.EmuELEC-H728.aarch64-4/toolchain/bin:/usr/bin:/bin \
 -v /home/ubuntu/build/emuelec:/build:ro -v "$S":/h728-cold-start-20261012 \
 -v "$S/kernel-handoff-source":/build/build.EmuELEC-H728.aarch64-4/build/linux-6.18.38 \
 h728-emuelec-builder:latest /bin/bash -c '
 set -euo pipefail
 s=/h728-cold-start-20261012
 cd /build/build.EmuELEC-H728.aarch64-4/build/linux-6.18.38
 export ARCH=arm64 CROSS_COMPILE=aarch64-libreelec-linux-gnueabi-
 # Restore generated headers after the earlier QEMU-only configuration.
 make olddefconfig
 test "$(sha256sum .config | cut -d" " -f1)" = e73aeb9a99ae78ac41c3e54bbca8ffc47b900714b128e74f2c04374767cc48d7
 make -j4 Image
 cp arch/arm64/boot/Image "$s/KERNEL-BOOT-SD-KEEPAWAKE-CANDIDATE"
 ${CROSS_COMPILE}objcopy --strip-debug vmlinux "$s/vmlinux-boot-sd-keepawake.elf"
 cp System.map "$s/boot-sd-keepawake.System.map"
 grep -q h728_axp323_prepare_polyphase System.map
 if grep -E "h728_(linux_(gpio|stage|trace)|deferred_probe_stage|kernel_entry_trace)" System.map; then exit 7; fi
 sha256sum .config "$s/KERNEL-BOOT-SD-KEEPAWAKE-CANDIDATE" "$s/vmlinux-boot-sd-keepawake.elf"
 echo BOOT_SD_KEEPAWAKE_REAL_BUILD_PASS_NOT_HARDWARE_ACCEPTANCE
 '
