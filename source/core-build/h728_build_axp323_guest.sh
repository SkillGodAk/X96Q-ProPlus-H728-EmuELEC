#!/usr/bin/env bash
# Single board-initialization candidate. No SD, eMMC or raw bootloader access.
set -euo pipefail
stage=/home/ubuntu/h728-cold-start-20261012
tree="$stage/kernel-handoff-source"
source_file="$tree/drivers/regulator/axp20x-regulator.c"
backup="$stage/h728-pre-axp323-20261013"
patcher="$stage/h728_axp323_polyphase_candidate.py"
verifier="$stage/verify_h728_axp323_helper.py"
candidate="$stage/h728-axp323-candidate.c"
manifest="$stage/h728-axp323-source.json"
log="$stage/kernel-axp323-build.log"
rc_file="$stage/kernel-axp323-build.rc"
new_image="$stage/KERNEL-AXP323-PHASE-UNDEPLOYED"
new_elf="$stage/vmlinux-axp323-phase.elf"
test "$(id -un)" = ubuntu
test "$(pwd -P)" = "$stage"
for file in "$backup" "$candidate" "$manifest" "$log" "$rc_file" "$new_image" "$new_elf"; do
  if [[ -e "$file" ]]; then echo "AXP323_DUPLICATE_RUN_REFUSED $file"; exit 4; fi
done
test -f "$tree.copy-ready"
test -f "$stage/h728_build_parts.sh"
grep -q '^CONFIG_REGULATOR_AXP20X=y$' "$tree/.config"
grep -q 'regmap_read_bypassed' "$tree/include/linux/regmap.h"
printf '%s  %s\n' \
  3701b610aa7bec4be3406407783efe23258a7934aac86cf2c8932401e2968bf8 "$patcher" \
  6ad6d698bbf039b46460826586b073720e32e3727888f6129c4070af9306ca4b "$verifier" \
  a06555a9d389bb944a9e13393f00bfb373813e864816d52e1333852b748ffa4f "$source_file" \
  8edcbb7ce27f429f1cbfd6ce364ddee734f1bd5accd08ce7725303585247e085 "$tree/drivers/base/dd.c" \
  b6b8409eac39928df35f03151e4366b78c9f7b00239d0e27fc1ebf306a99a753 "$tree/arch/arm64/boot/dts/allwinner/sun55i-h728-x96qpro+.dts" \
  1f25593cc5114fa5154284de6b7fd2d2fc7847a57d88223443c13f72b045de88 "$tree/drivers/mfd/axp20x.c" \
  7afc90e6b75fae92704bbcf7ba97347e73652bcf8abbd98b21834dd97f707668 "$stage/KERNEL-FINAL-HANDOFF-TRACE" \
  3f2ca8dbb5240d6b07f901f941b764a0188c162999df1ddf1e14a45a9c255d34 "$stage/vmlinux-final-handoff.elf" \
  | sha256sum -c -
python3 "$patcher" "$source_file" --output "$candidate" --manifest "$manifest"
printf '%s  %s\n' 74df776fdd134a5e067ff0809e70cd98fa8d16d936797145ba79825a7de0d6b5 "$candidate" | sha256sum -c -
docker run --rm --network none --user "$(id -u):$(id -g)" \
  -e PATH=/usr/bin:/bin -v "$stage":/h728-cold-start-20261012 \
  h728-emuelec-builder:latest \
  python3 /h728-cold-start-20261012/verify_h728_axp323_helper.py \
  /h728-cold-start-20261012/h728-axp323-candidate.c \
  --report /h728-cold-start-20261012/h728-axp323-helper-test.json
install -d -m 700 "$backup"
cp -p "$source_file" "$backup/axp20x-regulator.c"
cp -p "$stage/KERNEL-FINAL-HANDOFF-TRACE" "$backup/KERNEL"
cp -p "$stage/vmlinux-final-handoff.elf" "$backup/vmlinux.elf"
cp -p "$stage/kernel-final-handoff.System.map" "$backup/System.map"
completed=0
restore() {
  if [[ "$completed" -ne 1 ]]; then
    cp "$backup/axp20x-regulator.c" "$source_file"
    cp "$backup/KERNEL" "$stage/KERNEL-FINAL-HANDOFF-TRACE"
    cp "$backup/vmlinux.elf" "$stage/vmlinux-final-handoff.elf"
    cp "$backup/System.map" "$stage/kernel-final-handoff.System.map"
    echo AXP323_FAILED_RESTORED_V2_SOURCE_AND_OUTPUTS
  fi
}
trap restore EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM
cp "$candidate" "$source_file"
set +e
bash "$stage/h728_build_parts.sh" kernel >"$log" 2>&1
rc=$?
set -e
printf '%s\n' "$rc" >"$rc_file"
if [[ "$rc" -ne 0 ]]; then tail -n 50 "$log"; exit "$rc"; fi
if grep -q 'WARNING: modpost' "$log"; then tail -n 50 "$log"; exit 5; fi
grep -q 'H728_KERNEL_BUILD_PASS' "$log"
grep -q 'h728_axp323_prepare_polyphase' "$stage/kernel-final-handoff.System.map"
cp "$stage/KERNEL-FINAL-HANDOFF-TRACE" "$new_image"
cp "$stage/vmlinux-final-handoff.elf" "$new_elf"
printf '%s  %s\n' 74df776fdd134a5e067ff0809e70cd98fa8d16d936797145ba79825a7de0d6b5 "$source_file" | sha256sum -c -
sha256sum "$new_image" "$new_elf"
cat "$stage/h728-axp323-helper-test.json"
completed=1
echo H728_AXP323_KERNEL_BUILD_PASS_UNDEPLOYED
