#!/bin/bash
set -euo pipefail
stage=/home/ubuntu/h728-cold-start-20261012
cd "$stage"
test ! -e clean-release-build.log
exec >clean-release-build.log 2>&1
trap 'rc=$?; printf "%s\n" "$rc" > clean-release-build.rc' EXIT
python3 clean_release_prepare.py
docker run --rm --network none --user "$(id -u):$(id -g)" \
 -e CCACHE_DISABLE=1 -e PATH=/build/build.EmuELEC-H728.aarch64-4/toolchain/bin:/usr/bin:/bin \
 -v /home/ubuntu/build/emuelec:/build:ro -v "$stage":/h728-cold-start-20261012 \
 -v "$stage/kernel-handoff-source":/build/build.EmuELEC-H728.aarch64-4/build/linux-6.18.38 \
 h728-emuelec-builder:latest /bin/bash -c '
 set -euo pipefail
 s=/h728-cold-start-20261012
 cd "$s/atf-trace-source"
 prefix=aarch64-libreelec-linux-gnueabi-
 CC=${prefix}gcc CPP=${prefix}gcc AS=${prefix}gcc LD=${prefix}gcc CROSS_COMPILE=$prefix LDFLAGS="" CFLAGS="" \
 make -j4 PLAT=sun55i_a523 BUILD_BASE="$s/atf-clean-release-output" BUILD_STRING=02b45fe-dirty SOURCE_DATE_EPOCH=1791203453 H728_UART_FLUSH_BOUNDED=1 bl31
 cp "$s/atf-clean-release-output/sun55i_a523/release/bl31.bin" "$s/ATF-CLEAN-RELEASE.bin"
 cd "$s/uboot-trace-source"
 make -j4 CROSS_COMPILE=$prefix HOSTCC=/usr/bin/gcc HOSTCXX=/usr/bin/g++ BL31="$s/ATF-CLEAN-RELEASE.bin" \
 HOSTCFLAGS="-O2 -I/build/build.EmuELEC-H728.aarch64-4/toolchain/include" \
 HOSTLDFLAGS="-L/build/build.EmuELEC-H728.aarch64-4/toolchain/lib -Wl,-rpath,/build/build.EmuELEC-H728.aarch64-4/toolchain/lib"
 cp u-boot-sunxi-with-spl.bin "$s/UBOOT-CLEAN-RELEASE.bin"
 ${prefix}objcopy --strip-debug u-boot "$s/uboot-clean-release.elf"
 if ${prefix}nm u-boot | grep -E "h728_(bootstage|direct|entry_trace|final_trace|eret_trace)";then exit 7;fi
 if ${prefix}nm "$s/atf-clean-release-output/sun55i_a523/release/bl31/bl31.elf" | grep "h728_atf";then exit 7;fi
 cd /build/build.EmuELEC-H728.aarch64-4/build/linux-6.18.38
 export ARCH=arm64 CROSS_COMPILE=$prefix
 make -j4 Image
 cp arch/arm64/boot/Image "$s/KERNEL-CLEAN-AXP323"
 ${prefix}objcopy --strip-debug vmlinux "$s/vmlinux-clean-axp323.elf"
 cp System.map "$s/clean-kernel.System.map"
 grep -q "h728_axp323_prepare_polyphase" System.map
 if grep -E "h728_(linux_(gpio|stage|trace)|deferred_probe_stage|kernel_entry_trace)" System.map;then exit 7;fi
 sha256sum "$s/KERNEL-CLEAN-AXP323" "$s/vmlinux-clean-axp323.elf" "$s/UBOOT-CLEAN-RELEASE.bin" "$s/ATF-CLEAN-RELEASE.bin"
 echo CLEAN_RELEASE_ALL_REAL_BUILDS_PASS
 '
